# coding: utf-8
#!/usr/bin/env python

__author__      = "Viktor Dmitriyev"
__license__     = "MIT"
__version__     = "1.2.0"
__updated__     = "06.08.2018"
__created__     = "03.08.2018"
__description__ = "Get citations for the data of 'Hochschulbibliografie' (Universities Publication Bibliography) of UOL."

import os
import csv
import sys
import uuid
import json
import time
import codecs
import random
import shutil
import argparse
import cStringIO
#import pandas as pd

from habanero import Crossref

# helpers
import helpers as hlp

# importing custom libraries
try:
    import scholar
except:

    if sys.version_info[0] >= 3:
        from urllib.request import urlretrieve
    else:
        from urllib import urlretrieve

    target_path = 'https://raw.githubusercontent.com/ckreibich/scholar.py/master/scholar.py'
    target_name = 'scholar.py'
    urlretrieve (target_path, target_name)
finally:
    import scholar

# settings
CITATIONS_DIR = 'citations'
CITATIONS_JSONDB_NAME = 'citations-db.json'
CITATIONS_MERGEDDB_NAME = 'db-merged-with-citations.csv'

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UOLBibliographyCitator:
    """ Get citations for data of 'Hochschulbibliografie' ((Universities Publication Bibliography) of UOL. """

    def __init__(self):
        """ Initial method. """

        self.logger = hlp.custom_logger(logger_name='citations')

        if not os.path.exists(CITATIONS_DIR):
            os.makedirs(CITATIONS_DIR)

    def dump_citations(self, json_content):
        ''' Save citations from the JSON object locally'''

        path_citations_db = os.path.join(CITATIONS_DIR, CITATIONS_JSONDB_NAME)

        # make a copy of the existing file
        if os.path.isfile(path_citations_db):
            os.rename(path_citations_db, path_citations_db + '-' + str(uuid.uuid4())[:8])

        # sort by key before dumping
        json_content_sorted = {}
        sorted_keys = sorted(json_content.keys())
        for key in sorted_keys:
            json_content_sorted[key] = json_content[key]

        # dump the content
        with open(path_citations_db, 'w') as _f_dump:
            _f_dump.write(json.dumps(json_content_sorted, indent=2))

    def load_citations(self):
        ''' Load citations in form of a JSON object.'''

        citations_db = {}

        path_citations_db = os.path.join(CITATIONS_DIR, CITATIONS_JSONDB_NAME)
        try:
            with open(path_citations_db) as json_data:
                citations_db = json.load(json_data)
        except Exception as ex:
            self.logger.error('[e] Exception happened: {0}'.format(str (ex)))

        return citations_db

    def read_csv(self, f_input):
        ''' Read data from CSV'''

        # the pandas way
        #data = pd.read_csv(f_input, sep=',')

        # the vanilla way
        data = []
        with open(f_input, 'rb') as csvfile:
            csv_reader = UnicodeReader(csvfile)
            for index, row in enumerate(csv_reader):
                if index > 0:
                    data.append(row)

        return data

    def citation_via_scholar(self, querier, row):
        ''' Get citation from Google Scholar
            Due to all hacks/tricks, crawling via GS is not working stable, even by using public proxies.
        '''

        result = None

        def random_proxy_id():
            ''' Retrieve a random index proxy (the index is needed to delete it if not working)'''
            list_id = random.randint(0, len(self.proxies_ids) - 1)
            return self.proxies_ids[list_id]

        try:
            # # get proxy
            # # -> requires modified version of the scholar
            # proxy_id = None
            # if self.proxies_ids != []:
            #     proxy_id = random_proxy_id()

            # prepare scholar query
            query = scholar.SearchScholarQuery()
            query.set_author(row[1])  # author name
            query.set_words(row[2])   # publication title

            # -> requires modified version of the scholar
            #querier.send_query(query, proxy_id) # send query
            querier.send_query(query) # send query

            # save citation as JSON
            result = {'source': 'GS',
                      'value': querier.articles[0]['num_citations']}
        # except IndexError:
        #     self.proxies_ids.remove(proxy_id)
        #     self.logger.error('Remove proxy id (Google Scholar): {0}.'.format(proxy_id))
        except Exception as ex:
            self.logger.error('Exception while getting number of citations (Google Scholar): {0}.\nTitle:{1}'.\
                              format(ex, row[2].encode('utf-8')))

        return result

    def citation_via_crossref(self, cr, row):
        ''' Get citation from Crossref'''

        result = None
        query = row[2] + ' ' + row[1]

        try:
            response = cr.works(query = query, limit = 1)
            if response['message']['items']:
                result = {'source': 'CR',
                          'value': response['message']['items'][0]['is-referenced-by-count']}
        except Exception as ex:
            self.logger.error('Exception while getting number of citations (Crossref): {0}.\nTitle:{1}'.\
                            format(ex, row[2].encode('utf-8')))

        return result

    def crawl_citations(self, f_input):
        """ Crawls citations for each publication.

        Arguments:
            f_input {str} -- input file name
        """

        # load data
        df_original = self.read_csv(f_input)
        citations_db = self.load_citations()

        # prepare scholar crawler
        querier = scholar.ScholarQuerier()
        settings = scholar.ScholarSettings()
        querier.apply_settings(settings)

        # # -> requires modified version of the scholar
        # self.proxies = querier.proxies
        # self.proxies_ids = [x for x in range(len(querier.proxies))]

        # prepare Crossref crawler
        cr = Crossref()

        crawls_cnt = [0, 0]

        #for index, row in df_original.iterrows(): # pandas way
        for index, row in enumerate(df_original):

            if row[2] not in citations_db:
                citations_db[row[2]] = {}

            # crawl GS
            if 'GS' not in citations_db[row[2]]:
                crawls_cnt[0]+=1
                citation_gs = self.citation_via_scholar(querier, row)
                if citation_gs is not None:
                    citations_db[row[2]]['GS'] = citation_gs

            # crawl CR
            if 'CR' not in citations_db[row[2]]:
                crawls_cnt[1]+=1
                citation_cr = self.citation_via_crossref(cr, row)
                if citation_cr is not None:
                    citations_db[row[2]]['CR'] = citation_cr

            # save crawled DB after N titles (GS and CR separate) processed and sleep
            if     (crawls_cnt[0] % 5 == 0 and crawls_cnt[0] != 0)\
                or (crawls_cnt[1] % 15 == 0 and crawls_cnt[1] != 0):
                sleep_interval = random.randrange(2, 7, 1)
                self.logger.info('Save intermediate results and sleep for {0}. Total processed so far: {1}'.format(sleep_interval, index))
                time.sleep(sleep_interval)
                self.dump_citations(citations_db)

        self.dump_citations(citations_db)

    def merge_citations(self, f_input):
        """ Merge citations for each publication.

        Arguments:
            f_input {str} -- input file name
        """

        # load data
        df_original = self.read_csv(f_input)
        citations_db = self.load_citations()
        results = []
        # key = "Reflexive Grounded Theory"
        # print (citations_db[key])
        # return
        #for index, row in df_original.iterrows(): # pandas way
        for index, row in enumerate(df_original):
            key = row[2]
            cur_row = row

            #print(index, row[2])

            if key in citations_db:

                if 'GS' in citations_db[key]:
                    if citations_db[key]['GS'] != None:
                        cur_row.append(str(citations_db[key]['GS']['value']))
                    else:
                        cur_row.append(str(-1))
                else:
                    cur_row.append(str(-1))

                if 'CR' in citations_db[key]:
                    if citations_db[key]['CR'] != None:
                        cur_row.append(str(citations_db[key]['CR']['value']))
                    else:
                        cur_row.append(str(-1))
                else:
                    cur_row.append(str(-1))

            results.append(cur_row)

        #DELIMETER = ';'
        DELIMETER = '","'

        header_row = ['Fach', 'Autor/in', 'Titel', 'Seiten', 'Sprache',
                     'ZahlWoerterTitel', 'Typ', 'Meldetag', 'Punktzahl', 'ZahlOldenburgerAutoren',
                     'Jahr', 'GoogleScholar', 'Crossref']
        header = DELIMETER.join(header_row)
        data_csv = '"' + header + '"' + '\n'
        #resulting_csv = header + '\n'

        for row in results:
            #csv_row = DELIMETER.join(str(value).replace('"', "") for value in row)
            csv_row = DELIMETER.join(value.replace('"', "") for value in row)
            data_csv +=  '"' + csv_row + '"' + '\n'
            #resulting_csv +=   csv_row + '\n'

        # save CSV
        path_merged_citations_db = os.path.join(CITATIONS_DIR, CITATIONS_MERGEDDB_NAME)

        # saving to file
        _file = codecs.open(path_merged_citations_db, 'w', 'utf-8')
        _file.write(data_csv)
        _file.close()

        # with open(path_merged_citations_db, 'w') as _f_dump:
        #     _f_dump.write(resulting_csv)

def main(input, action):
    """ Main method that starts other methods.

    Arguments:
        input {str} -- input file name
    """

    uol_bib_citations = UOLBibliographyCitator()

    if action == 'CRAWL':
        uol_bib_citations.crawl_citations(f_input=input)

    if action == 'MERGE':
        uol_bib_citations.merge_citations(f_input=input)

if __name__ == '__main__':


    # sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    # sys.stderr = codecs.getwriter('utf8')(sys.stderr)

    # fetching input parameters
    parser = argparse.ArgumentParser(description='{0}\nVersion - {1}'.format(__description__, __version__))

    # input file
    parser.add_argument(
        '--input',
        dest='input',
        help='input with cleaned and unique data in CSV')
    parser.set_defaults(mergedata='uolbibliography-2008-2016-merged-cleaned-unique.csv')

    # mode
    actions = ('CRAWL', 'MERGE')
    parser.add_argument(
        '--action',
        help='specifies action type (default "CRAWL"), must one of the following {0}'.format(actions))
    parser.set_defaults(action='CRAWL')

    # parse input parameters
    args = parser.parse_args()

    # verifying given parameters
    if args.action not in actions:
        print('[x] set proper launching action: {0}'.format(actions))
        exit(0)

    main(args.input, args.action.upper())

