# coding: utf-8
#!/usr/bin/env python

__author__      = "Viktor Dmitriyev"
__license__     = "MIT"
__version__     = "1.1.0"
__updated__     = "03.08.2018"
__created__     = "03.08.2018"
__description__ = "Get citations for data of 'Hochschulbibliografie' (Universities Publication Bibliography) of UOL."

import os
import sys
import uuid
import json
import time
import shutil
import argparse
import pandas as pd

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
            print ('Exception happened: {0}'.format(str(ex)))

        return citations_db

    def crawl_citations(self, f_input):
        """ Crawls citations for each publication.

        Arguments:
            f_input {str} -- input file name
        """

        if not os.path.exists(CITATIONS_DIR):
            os.makedirs(CITATIONS_DIR)

        # load data
        df_original = pd.read_csv(f_input, sep=',')
        citations_db = self.load_citations()

        # prepare scholar crawler
        querier = scholar.ScholarQuerier()
        settings = scholar.ScholarSettings()
        querier.apply_settings(settings)
        crawls_cnt = 0

        for index, row in df_original.iterrows():

            if row[2] not in citations_db:

                crawls_cnt+=1
                citations_db[row[2]] = 0

                # prepare scholar query
                query = scholar.SearchScholarQuery()
                query.set_author(row[1]) # author name
                query.set_words(row[2])  # publication title
                querier.send_query(query)# send query

                # save citation into JSON
                try:
                    citations_db[row[2]] = querier.articles[0]['num_citations']
                except Exception as ex:
                    citations_db[row[2]] = -1
                    print('[e] Exception while getting number of citations: {0}.\nTitle:{1}'.format(ex, row[2]))

            # save crawled DB after N titles processed and sleep
            if index % 25 == 0:
                print ('[i] Save intermediate results and sleep. Total processed so far: {0}'.format(index))
                time.sleep(1)
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

