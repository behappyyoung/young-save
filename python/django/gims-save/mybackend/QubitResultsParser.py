# coding: utf-8
#!/usr/bin/env python
##
# NAME: QubitResultsParser.py
# Description: Parse Qubit results (EXCEL file) to retrieve DNA Concentrations by sample.
# Author: SHC
# Version: 0.1
##

import pandas as pd
from operator import itemgetter
import math
import time
import argparse
import os.path
import sys

class QubitResultsParser(object):

    min_conc_threshold = 0.1
    max_conc_threshold = 1000

    def parseResults(self, fileName, rerun=False):
        return_values_dict = {}
        status = 'PASS'
        dilution_factor = 10;

        columnnames = [u'Run ID', u'Samples', u'Original sample conc.', u'Units', u'Sample Volume (µL)',  u'Dilution Factor',u'Std 1 RFU', u'Std 2 RFU', u'Std 3 RFU', u'Excitation', u'Emission', u'Green RFU', u'Far Red RFU']



        try:
            os.path.isfile(fileName);
            os.path.exists(fileName);

            dataframe = pd.read_excel(fileName, sheetname=0)
            #print dataframe.columns

            for index, row in dataframe.iterrows():
                conc = row[columnnames[2]]
                if rerun is True:
                    conc = conc * dilution_factor
                    status = 'PASS'
                else:
                    if conc < self.min_conc_threshold:
                        status = 'FAILED'
                    elif conc > self.max_conc_threshold:
                        status = 'TOO HIGH'
                    else:
                        status = 'PASS'

                values_list = []
                values_list.append(row[columnnames[0]])
                values_list.append(row[columnnames[1]])
                values_list.append(conc)
                values_list.append(row[columnnames[3]])
                values_list.append(status)

                return_values_dict[index+1] = values_list
                #print index, row[columnnames[0]], row[columnnames[1]], row[columnnames[2]], row[columnnames[3]], row[columnnames[4]]

            return return_values_dict

        except Exception as e:
            raise e

    def __init__(self):
        min_conc_threshold = 0.1
        max_conc_threshold = 1000

    @classmethod
    def main(cls, args):

        try:
            fileName = "/Users/s0199669/cgsdev/gims/staticfiles/IMAGES/Gcloud/Example_QubitDataFile.xls"
            os.path.isfile(fileName);
            os.path.exists(fileName);
            qubitResultsParser = QubitResultsParser()
            return_dict = qubitResultsParser.parseResults(fileName)
            for index in return_dict:
                list = return_dict.get(index)
                print list[0], list[1], list[2], list[3], list[4]

        except Exception as e:
            print(e)
            exit(1)

if __name__ == '__main__':
    import sys
    QubitResultsParser.main(sys.argv)