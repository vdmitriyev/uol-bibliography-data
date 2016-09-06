# coding: utf-8
#!/usr/bin/env python

__author__      = "Viktor Dmitriyev"
__copyright__   = "Copyright 2016, Viktor Dmitriyev"
__credits__     = ["Viktor Dmitriyev"]
__license__     = "MIT"
__version__     = "1.0.0"
__email__       = ""
__status__      = "test"
__date__        = "26.08.2016"
__description__ = "Plotter for data of 'Hochschulbibliografie' (Universities Publication Bibliography) of UOL."

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt

#
import helpers as hlp

# settings

PLOTS_DIR = 'plots'

class UOLBibliographyDataPlotter:
    """ Plotter for data of 'Hochschulbibliografie' ((Universities Publication Bibliography) of UOL. """

    def __init__(self):
        """ Initial method. """

        self.logger = hlp.custom_logger(logger_name='cleaner')

    def validate_file_name(self, file_name):
        """ Removes all symbols that are not file name conform.

        Args:
            file_name: name of the file to be validated
        Returns:
            valid name of the file
        """

        valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        file_name = ''.join(c for c in file_name if c in valid_chars)
        return file_name

    def plotter(self, f_input):
        """ Plotter of data from CSV with bibliography.

        Arguments:
            f_input {str} -- input file name
        """

        if not os.path.exists(PLOTS_DIR):
            os.makedirs(PLOTS_DIR)

        df_original = pd.read_csv(f_input, sep=',')

        def plot_by_year_and_field(df):
            """ Plotting within each field publications/articles by year."""

            self.logger.info(plot_by_year_and_field.__doc__)

            fig, ax = plt.subplots()
            grouped = df.groupby(['Fach'])
            #grouped = df.groupby(['Autor/in'])

            for name, group in grouped:
                self.logger.info('Plotting - {0}'.format(name))
                if name != '%fach%':
                    ax.cla()
                    grouped_tmp = group.groupby(['Jahr']).count()
                    plot_tmp = grouped_tmp.plot(kind='bar', title = name, ax=ax, legend=False)
                    fig.savefig(os.path.join(PLOTS_DIR, 'bar-plot-{0}.png'.format(self.validate_file_name(name))))

            ax.cla()
            fig.clf()
            #fig.close()

        def plot_top_authors(df, k_authors = 30):
            """Plotting within each field publications/articles by year.

            One publication may have more that one author.

            Arguments:
                df {pandas.DataFrame} -- input data set

            Keyword Arguments:
                k_authors {number} -- top K authors to plot (default: {30})
            """

            self.logger.info('Executing method.\n{0}'.format(plot_top_authors.__doc__))

            grouped = df.groupby(['Autor/in']).count()

            grouped.columns = ['total']
            total_authors = len(grouped) - 1    # because of field with '%'
            self.logger.info('Total authors: {0}'.format(total_authors))

            grouped = grouped.sort_values(by='total', ascending=False).head(k_authors)

            fig, ax = plt.subplots()
            fig.set_size_inches((18.5 * k_authors) / 30, 12.5, forward=True)
            grouped.plot(kind='bar', ax=ax, legend=False, edgecolor='b',
                         title = 'Top {0} authors presented. In total there are {1} authors.'.format(k_authors, total_authors)
                        )

            for p in ax.patches:
                legend_text = str(p.get_height())
                x_delta = 0.15
                if len(legend_text) < 5: x_delta = 0.08
                ax.annotate(legend_text, xy=(p.get_x() - x_delta, p.get_height() + 0.5))

            fig.tight_layout()
            fig.savefig(os.path.join(PLOTS_DIR, 'top-k-authors.png'))
            ax.cla()
            fig.clf()


        def plot_total_articles_per_authors(df):
            """Plotting total articles per all authors.

            One publication may have more that one author.

            Arguments:
                df {pandas.DataFrame} -- input data set
            """

            self.logger.info('Executing method.\n{0}'.format(plot_total_articles_per_authors.__doc__))

            grouped = df.groupby(['Autor/in']).count()
            grouped.columns = ['total']
            total_publications = int(grouped.sum()) - 1 # because of field with '%'
            total_authors = len(grouped) - 1            # because of field with '%'
            avg = total_publications / total_authors

            self.logger.info('Total authors: {0}'.format(total_authors))

            grouped = grouped.sort_values(by='total', ascending=False)

            fig, ax = plt.subplots()
            fig.set_size_inches(20, 12.5, forward=True)
            grouped.plot(kind='hist', ax=ax, bins=200, legend=False, #edgecolor='b',
                         title = 'There are authors: {0}; publications (not unique): {1}; average : {2}.'.format(total_authors, total_publications, avg)
                         )
            fig.tight_layout()
            fig.savefig(os.path.join(PLOTS_DIR, 'total-articles-per-author-hist.png'))
            ax.cla()
            fig.clf()

        df_fach = df_original[['Fach', 'Jahr']]
        #df_fach = df_original[['Autor/in', 'Jahr']]
        #plot_by_year_and_field(df_fach)

        df_authors = df_original[['Autor/in', 'Jahr']]

        plot_top_authors(df_authors, k_authors = 300)
        plot_total_articles_per_authors(df_authors)

def main(input):
    """ Main method that starts other methods.

    Arguments:
        input {str} -- input file name
    """

    uol_bib_plotter = UOLBibliographyDataPlotter()
    uol_bib_plotter.plotter(f_input=input)

if __name__ == '__main__':

    # fetching input parameters
    parser = argparse.ArgumentParser(description='{0}\nVersion - {1}'.format(__description__, __version__))

    # input file
    parser.add_argument(
        '--input',
        dest='input',
        help='input with cleaned and unique data in CSV')
    parser.set_defaults(mergedata='uolbibliography-2008-2015-merged-cleaned-unique.csv')

    # parse input parameters
    args = parser.parse_args()

    main(args.input)

