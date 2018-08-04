# coding: utf-8
#!/usr/bin/env python

__author__      = "Viktor Dmitriyev"
__license__     = "MIT"
__version__     = "1.1.0"
__updated__     = "03.08.2018"
__created__     = "03.08.2018"
__description__ = "Get citations for data of 'Hochschulbibliografie' (Universities Publication Bibliography) of UOL."

import os
import csv
import sys
import uuid
import json
import time
import random
import shutil
import argparse
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

import codecs, cStringIO

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

    def dump_citations(self, json_content):
        ''' Save citations from the JSON object locally'''

        path_citations_db = os.path.join(CITATIONS_DIR, CITATIONS_JSONDB_NAME)

        # make a copy of the existing file
        if os.path.isfile(path_citations_db):
            os.rename(path_citations_db, path_citations_db + '-' + str(uuid.uuid4())[:8])

        # dump the content
        with open(path_citations_db, 'w') as _f_dump:
            _f_dump.write(json.dumps(json_content, indent=2))

    def load_citations(self):
        ''' Load citations in form of a JSON object.'''

        citations_db = {}

        path_citations_db = os.path.join(CITATIONS_DIR, CITATIONS_JSONDB_NAME)
        try:
            with open(path_citations_db) as json_data:
                citations_db = json.load(json_data)
        except Exception as ex:
            print ('Exception happened: {0}'.format(str (ex)))

        return citations_db

    def read_csv(self, f_input):
        ''' Read data from CSV'''

        # the pandas way
        #data = pd.read_csv(f_input, sep=',')

        # the vanilla way
        data = []
        with open(f_input, 'rb') as csvfile:

            # no UTF-8
            #csv_reader = csv.reader(csvfile, delimiter=',')
            #csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),**kwargs)
            # for index, row in enumerate(csv_reader):
            #     if index > 0:
            #         data.append(row)

            csv_reader = UnicodeReader(csvfile)
            for index, row in enumerate(csv_reader):
                if index > 0:
                    data.append(row)

        return data

    def citation_via_scholar(self, querier, row):
        ''' Get citation from Google Scholar'''

        result = None

        try:
            # prepare scholar query
            query = scholar.SearchScholarQuery()
            query.set_author(row[1]) # author name
            query.set_words(row[2])  # publication title
            querier.send_query(query)# send query

            # save citation as JSON
            result = {'source': 'GS',
                      'value': querier.articles[0]['num_citations']}
        except Exception as ex:
            print('[e] Exception while getting number of citations (Google Scholar): {0}.\nTitle:{1}'.format(ex, row[2]))

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
            print('[e] Exception while getting number of citations (Crossref): {0}.\nTitle:{1}'.format(ex, row[2]))

        return result


    def crawl_citations(self, f_input):
        """ Crawls citations for each publication.

        Arguments:
            f_input {str} -- input file name
        """

        if not os.path.exists(CITATIONS_DIR):
            os.makedirs(CITATIONS_DIR)

        # load data
        df_original = self.read_csv(f_input)
        citations_db = self.load_citations()

        # prepare scholar crawler
        querier = scholar.ScholarQuerier()
        settings = scholar.ScholarSettings()
        querier.apply_settings(settings)

        # prepare Crossref
        cr = Crossref()

        #for index, row in df_original.iterrows(): # pandas way
        for index, row in enumerate(df_original):

            if row[2] not in citations_db:

                #crawls_cnt+=1
                citations_db[row[2]] = {}

                # citation = self.citation_via_scholar(querier, row)

                # if citation is not None:
                #     citations_db[row[2]] = citation
                # else:

                citation = self.citation_via_crossref(cr, row)

                citations_db[row[2]] = citation

            # save crawled DB after N titles processed and sleep
            if index % 15 == 0:
                sleep_interval = random.randrange(5, 13, 1)
                print ('[i] Save intermediate results and sleep for {0}. Total processed so far: {1}'.format(sleep_interval, index))
                time.sleep(sleep_interval)
                self.dump_citations(citations_db)

def main(input):
    """ Main method that starts other methods.

    Arguments:
        input {str} -- input file name
    """

    uol_bib_citations = UOLBibliographyCitator()
    uol_bib_citations.crawl_citations(f_input=input)

if __name__ == '__main__':

    # fetching input parameters
    parser = argparse.ArgumentParser(description='{0}\nVersion - {1}'.format(__description__, __version__))

    # input file
    parser.add_argument(
        '--input',
        dest='input',
        help='input with cleaned and unique data in CSV')
    parser.set_defaults(mergedata='uolbibliography-2008-2016-merged-cleaned-unique.csv')

    # parse input parameters
    args = parser.parse_args()

    main(args.input)

