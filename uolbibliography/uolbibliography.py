# coding: utf-8
#!/usr/bin/env python

__author__     = "Viktor Dmitriyev"
__copyright__ = "Copyright 2016, Viktor Dmitriyev"
__credits__ = ["Viktor Dmitriyev"]
__license__ = "MIT"
__version__ = "1.0.0"
__email__     = ""
__status__     = "test"
__date__    = "01.08.2016"
__description__ = "Crawler for the 'Hochschulbibliografie' ((Universities Publication Bibliography) of UOL."

import os
import uuid
import json
import codecs
import locale
import urllib2
import argparse
import collections
from time import sleep
from pprint import pprint
from bs4 import BeautifulSoup

#
import helpers as hlp

# importing custom libraries
try:
    from helper_directory import DirectoryHelper
except:
    import urllib
    target_path = 'https://raw.githubusercontent.com/vdmitriyev/sourcecodesnippets/master/python/helper_directory/helper_directory.py'
    target_name = 'helper_directory.py'
    urllib.urlretrieve (target_path, target_name)
    from helper_directory import DirectoryHelper
finally:
    import helper_directory
    if helper_directory.__version__ != '1.0.0':
        print 'Wrong version of the library {0}. Check the version'.format(helper_directory.__file__)

# settings
SLEEP_TIME_IN_SECONDS = 2

class BSCrawler():
    """ Crawling the HTML page and fetching data into table forms."""

    UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'

    def __init__(self):
        """  Initial method that:

            - initiates helper class;
            - checks the temp directory existence;
        """
        self.logger = hlp.custom_logger()
        self.helper = DirectoryHelper()
        #self.helper.prepare_working_directory()
        try:
            self.work_dir = self.helper.work_dir
        except:
            self.work_dir = '__temp__'

        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

        self.logger.info('[i] files will be saved into folder "{0}"'.format(self.work_dir))

    def crawl(self, mergedata, urlfile=None, dispatcher=None):
        """Method that extracts urls from 'dispatcher' dictionary and process them.

        Args:
            urlfile: file that contains URLS to be processed
        """

        if dispatcher:
            self.dispatcher = dispatcher
            for url in self.dispatcher:
                self.logger.info('[i] following URL is going to be parsed:\n {0}'.format(url))
                self.main_url = url
                doc = self.download_document(url)
                self.dispatcher[url](self, doc)

        data = []
        if urlfile:
             with codecs.open(urlfile, 'r', encoding='utf8') as f_urls:
                for line in f_urls:
                    doc = self.download_document(line.strip())
                    data += self.process_uol_bibliography_tbl(doc)
                    sleep(SLEEP_TIME_IN_SECONDS)

        if mergedata:
            csv = self.data_as_csv(data)
            self.helper.save_file(os.path.join(self.work_dir, 'merged.csv'), csv)

    def download_document(self, url):
        """
            (obj,str) -> (str)

            Downloading html page and storing inside string.
        """

        html = None
        try:
            req = urllib2.Request(url=url, headers={'User-Agent': self.UA})
            hdl = urllib2.urlopen(req)
            html = hdl.read()
        except Exception as ex:
            self.logger.error('[e] exception: {0}, arguments: {1}'.format(ex.message, ex.args))

        return html

    # def save_images(self, img_list, folder):
    #     """
    #         (obj, list, str) -> None

    #         Saving images to the folders
    #     """

    #     img_dir = self.work_dir + folder + '\\'
    #     self.helper.create_directory_ondemand(img_dir)
    #     for img in img_list:
    #         img_full_url = img['src']
    #         if img['src'][:4] != 'http':
    #             img_full_url = self.main_url + img['src']
    #         img_extention = img_full_url[img_full_url.rfind('.'):]
    #         image = self.download_document(img_full_url)

    #         if image is not None:
    #             gen_img_name = img_dir + self.helper.gen_file_name(extention='')
    #             self.helper.save_img_file(gen_img_name + img_extention, image)
    #         else:
    #             self.logger.info('[i] this image is not found: {0}'.format(img_full_url))

    def data_as_csv(self, data, size = 8):
        """ Getting data as CSV. """

        resulting_csv = ''
        DELIMETER = '","'

        # adding header
        header_values = ['Fach', 'Autor/in', 'Titel', 'Typ', 'Meldetag', 'Punktzahl', ' ZahlOldenburgerAutoren', 'Jahr']
        header_row = DELIMETER.join(header_values)
        resulting_csv = '"' + header_row + '"' + '\n'

        for row in data:
            if len(row) == size:
                csv_row = DELIMETER.join(self.decode_abbreviations(row))
                resulting_csv +=  '"' + csv_row + '"' + '\n'

        return resulting_csv

    def decode_abbreviations(self, row, size = 8, lang = 'DE'):
        """ Decoding particular abbreviations within given data. """

        if size != 8: return None

        mapping = {}
        mapping['DE'] = {'AU':'Aufsatz', 'MO': 'Monographie', 'ZS':'Zeitschrift', 'SW': 'Sammelwerksbeitrag'}
        mapping['EN'] = {'AU':'Article', 'MO': 'Monograph', 'ZS':'Journal', 'SW': 'ContributionsToACollectiveWork'}

        if row[3] in mapping[lang]:
            row[3] = mapping[lang][row[3]]

        return row


    def process_uol_bibliography_tbl(self, doc, output_file_name = None):
        """ Processing given HTML to extract publication information from UOL's Hochschulbibliografie.

        Args:
            doc:    document to be processed
        """

        def is_valid_row(data_chunk):
            """ Validating any particular row given as input.

            Args:
                data_chunk: some random row

            Returns:
                True/False according to the validity of the data
            """

            if len(data_chunk) < 1: return False
            if 'Gesamtpunkte' in data_chunk[0]: return False
            return True

        bs_html = BeautifulSoup(doc, 'html5lib')

        prettified_html = bs_html.prettify()
        text_from_html = bs_html.get_text()

        # getting name of the file from HTML
        if output_file_name is None:
            div_tag = bs_html.find('div', attrs={'id' : 'inhalt', 'class':'floatbox'})
            h1_tag = div_tag.find('h1')
            if h1_tag is not None:
                output_file_name = h1_tag.get_text(separator=u' ')
            else:
                output_file_name = self.helper.gen_file_name(extention='')

        # getting data from HTML table
        data = []
        table = bs_html.find('table', attrs={'class':'infotabelle'})
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele]) # Get rid of empty values

        # cleaning table data
        cleaned_data = []
        for row in data:
            if is_valid_row(row):
                cleaned_data.append(row)

        csv = self.data_as_csv(cleaned_data)

        # text data for debugging, uncomment if needed
        # self.helper.save_file(os.path.join(self.work_dir, output_file_name + '.html'), prettified_html)
        # self.helper.save_file(os.path.join(self.work_dir, output_file_name + '.txt'), text_from_html)
        self.helper.save_file(os.path.join(self.work_dir, output_file_name + '.csv'), csv)

        return cleaned_data

def main(urlfile, mergedata):

    crawler = BSCrawler()

    if file is not None:
        crawler.crawl(urlfile=urlfile, mergedata=mergedata)

if __name__ == '__main__':

    # fetching input parameters
    parser = argparse.ArgumentParser(description='{0}\nVersion - {1}'.format(__description__, __version__))

    # url file
    parser.add_argument(
        '--urlfile',
        help='specifies file with URLS to be processed')
    parser.set_defaults(urlfile='uolbibliography-test.txt')

    # merge results into single CSV
    parser.add_argument(
        '--mergedata',
        dest='mergedata',
        action='store_true',
        help='setting this option starts merging all CSV into one')
    parser.set_defaults(mergedata=False)

    # parse input parameters
    args = parser.parse_args()

    main(args.urlfile, args.mergedata)
