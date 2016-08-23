# coding: utf-8
#!/usr/bin/env python

__author__     = "Viktor Dmitriyev"
__copyright__ = "Copyright 2016, Viktor Dmitriyev"
__credits__ = ["Viktor Dmitriyev"]
__license__ = "MIT"
__version__ = "1.0.0"
__email__     = ""
__status__     = "test"
__date__    = "23.08.2016"
__description__ = "Cleaner for data of 'Hochschulbibliografie' (Universities Publication Bibliography) of UOL."

import csv
import codecs
import argparse

#
import helpers as hlp

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

class UOLBibliographyDataCleaner:
    """ Cleaner for data of 'Hochschulbibliografie' ((Universities Publication Bibliography) of UOL. """

    def __init__(self):
        """ Initial method. """

        self.logger = hlp.custom_logger(logger_name='cleaner')
        #self.helper = DirectoryHelper()

    def is_consistent(self, data):
        """Checking data for consistency.

        Arguments:
            data {list} -- list of objects
        """

        EXPECTED_ELEMENTS_COUNT = 8

        for row in data:
            if len(row) != EXPECTED_ELEMENTS_COUNT:
                self.logger.error('Wrong amount of elements. Expected - {1}, actual - {1}'.format(len(row), EXPECTED_ELEMENTS_COUNT))
                return False

        self.logger.info('Right amount of elements found')
        return True

    def data_as_csv(self, data):
        """ Getting data as CSV. """

        resulting_csv = ''
        DELIMETER = '","'

        # adding header
        header_values = ['Fach',
                         'Autor/in',
                         'Titel',
                         'Seiten',
                         'Sprache',
                         'ZahlWoerterTitel',
                         'Typ',
                         'Meldetag',
                         'Punktzahl',
                         'ZahlOldenburgerAutoren',
                         'Jahr']

        header_row = DELIMETER.join(header_values)
        resulting_csv = '"' + header_row + '"' + '\n'

        required_size = len(header_values)
        for row in data:
            if len(row) == required_size:
                csv_row = DELIMETER.join(value.replace('"', "") for value in row)
                resulting_csv +=  '"' + csv_row + '"' + '\n'
            else:
                self.logger.warning('Length of rows are not equal. Expected - {0}, actual {1}'.format(required_size, len(row)))

        return resulting_csv

    def save_to_file(self, f_output, data):
        """ Save data to CSV file.

        Arguments:
            f_output {str} -- output file name
            data {list} -- data to be saved into CSV
        """

        data_csv = self.data_as_csv(data)

        # saving to file
        _file = codecs.open(f_output, 'w', 'utf-8')
        _file.write(data_csv)
        _file.close()

    def clean(self, f_input, f_output):
        """Clean data

        Arguments:
            f_input {str} -- input file name
            f_output {str} -- output file name
        """

        self.logger.info("Start with cleaning. Input {0}".format(f_input))

        def process_publication_title(title):
            i_begin = title.rfind('(')
            i_end = title.rfind(')')

            clean_title = title[:i_begin].strip()
            pages_amount = title[i_begin+1:i_end-2].strip()

            return clean_title, pages_amount

        def detect_language_v1(title):
            language = None
            try:
                from langdetect import detect
                language = detect(title)
            except Exception as ex:
                self.logger.warning('Exception with language detection: {0}'.format(str(ex)))

            return language

        # def detect_language_v2(title):
        #     language = None
        #     try:
        #         from langid.langid import LanguageIdentifier, model
        #         identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        #         language = identifier.classify(title)[0]
        #     except Exception as ex:
        #         self.logger.warning('Exception with language detection: {0}'.format(str(ex)))

        #     return language

        def print_languages_ios_639(langauge_set):
            try:
                from pycountry import languages
                result = ''
                for lang in langauge_set:
                    result += '{0}:{1}\n'.format(lang, languages.get(iso639_1_code=lang).name)
                return result
            except Exception as ex:
                self.logger.warning('Exception with language decoding according to ISO 693-1: {0}'.format(str(ex)))
            return None

        def decode_language_ios_639(lang):
            try:
                from pycountry import languages
                return languages.get(iso639_1_code=lang).name
            except Exception as ex:
                self.logger.warning('Exception with language decoding according to ISO 693-1: {0}'.format(str(ex)))
            return 'Unknown'

        raw_data = []

        with codecs.open(f_input, 'r', encoding='utf8') as f_in:
            csv_reader = unicode_csv_reader(f_in, delimiter=',', quotechar='"')
            for row in csv_reader:
                raw_data.append(row)

        from sets import Set
        unique_languages_v1 = Set()

        # getting
        if self.is_consistent(raw_data):
            clean_data = []
            for index, row in enumerate(raw_data):
                clean_row = []
                if index > 1:
                    clean_row.append(row[0])
                    clean_row.append(row[1])

                    # separating title and number of pages
                    clean_title = process_publication_title(row[2])
                    clean_row.append(clean_title[0])
                    clean_row.append(clean_title[1])

                    # approximate language of article
                    lang_v1 = detect_language_v1(clean_title[0])
                    lang_v1_decoded = decode_language_ios_639(lang_v1)
                    clean_row.append(lang_v1_decoded)

                    # debugging
                    unique_languages_v1.add(lang_v1)

                    # amount of words in title
                    clean_row.append(str(len(clean_title[0].split())))

                    # adding rest of data
                    clean_row.extend(row[3:])

                if len(clean_row) > 0:
                    clean_data.append(clean_row)

            # unique languages
            # self.logger.info(unique_languages_v1)
            # self.logger.info(print_languages_ios_639(unique_languages_v1))

            self.save_to_file(f_output, clean_data)
        else:
            self.logger.info("Data are not consistent.")

        self.logger.info("Done with cleaning. Check {0}".format(f_output))


def main(input, output):
    """ Main method that starts other methods.

    Arguments:
        input {str} -- input file name
        output {str} -- output file name
    """

    cleaner = UOLBibliographyDataCleaner()
    cleaner.clean(f_input=input, f_output=output)


if __name__ == '__main__':

    # fetching input parameters
    parser = argparse.ArgumentParser(description='{0}\nVersion - {1}'.format(__description__, __version__))

    # input file
    parser.add_argument(
        '--input',
        dest='input',
        help='input with raw original data in CSV')
    parser.set_defaults(mergedata='uolbibliography-merged.csv')

    # output file
    parser.add_argument(
        '--output',
        dest='output',
        help='output with cleaned data in CSV')
    parser.set_defaults(output='uolbibliography-clean.csv')


    # parse input parameters
    args = parser.parse_args()

    main(args.input, args.output)
