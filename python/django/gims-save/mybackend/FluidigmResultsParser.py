# coding: utf-8
#!/usr/bin/env python
##
# NAME: FluidigmResultsParser.py
# Description: Parse Fluidigm results (EXCEL file) to retrieve DNA Concentrations by sample.
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
import json

class FluidigmResultsParser(object):

    def parseResults(self, fileName, totalAssays=96, failThreshold=10):
        return_values_dict = {}
        status = 'PASS'
        columnnames = [u'ID', u'Assay', u'Allele X', u'Allele Y', u'Name', u'Type', u'Auto', u'Confidence', u'Final', u'Converted', u'Allele X.1', u'Allele Y.1']
        noCall = 'No Call'
        homX = 'XX'
        homY = 'YY'
        hetXY = 'XY'

        try:
            os.path.isfile(fileName);
            os.path.exists(fileName);

            dataframe = pd.read_excel(fileName, sheetname=0, skiprows=15)
            # print dataframe.columns
            results_dict = {}
            results_list=[]
            assayidlist = []
            assaynamelist = []
            alleleXlist = []
            alleleYlist = []
            samplenamelist = []

            calllist = []
            callconfidencelist = []
            callfinallist = []
            xintensitylist = []
            yintensitylist = []

            assaycount = 0
            sampleindex = 0
            totalassayfails = 0

            for index, row in dataframe.iterrows():

                if assaycount == totalAssays: # reset
                    sampleindex = sampleindex + 1
                    if sampleindex != 0: # if past the first sample insert the list into dict
                        results_dict['AssayID'] = assayidlist
                        results_dict['AssayName'] = assaynamelist
                        results_dict['AlleleX'] = alleleXlist
                        results_dict['AlleleY'] = alleleYlist
                        results_dict['SampleName'] = samplenamelist

                        results_dict['Call']  = calllist
                        results_dict['Confidence'] = callconfidencelist
                        results_dict['FinalCall'] = callfinallist
                        results_dict['XIntensity'] = xintensitylist
                        results_dict['YIntensity'] = yintensitylist
                        results_dict['TotalFailedAssays'] = totalassayfails
                        if totalassayfails > failThreshold:
                            status = 'ASSAYFAIL'
                        else:
                            status = 'ASSAYPASS'
                        results_dict['Status'] = status

                        jsonResultsString = json.dumps(results_dict)
                        return_values_dict[sampleindex] = jsonResultsString
                        #print sampleindex

                    results_dict = {}
                    assaycount = 0 #reset assaycount for next sample
                    totalassayfails = 0
                    assayidlist = []
                    assaynamelist = []
                    alleleXlist = []
                    alleleYlist = []
                    samplenamelist = []

                    calllist = []
                    callconfidencelist = []
                    callfinallist = []
                    xintensitylist = []
                    yintensitylist = []


                assayid = row[columnnames[0]]
                assayname = row[columnnames[1]]
                alleleX = row[columnnames[2]]
                alleleY = row[columnnames[3]]
                samplename = row[columnnames[4]]

                call = row[columnnames[6]]
                callconfidence = row[columnnames[7]]
                callfinal = row[columnnames[8]]
                xintensity = row[columnnames[10]]
                yintensity = row[columnnames[11]]

                assayidlist.append(assayid)
                assaynamelist.append(assayname)
                alleleXlist.append(alleleX)
                alleleYlist.append(alleleY)
                samplenamelist.append(samplename)

                calllist.append(call)
                callconfidencelist.append(callconfidence)
                callfinallist.append(callfinal)
                xintensitylist.append(xintensity)
                yintensitylist.append(yintensity)

                if call == noCall:
                    totalassayfails = totalassayfails + 1
                    results_list.append('FAIL')
                else:
                    results_list.append('PASS')

                assaycount = assaycount+1

            #last sample needs to added to the dictionary
            if totalAssays > 0:
                sampleindex = sampleindex + 1
                results_dict['AssayID'] = assayidlist
                results_dict['AssayName'] = assaynamelist
                results_dict['AlleleX'] = alleleXlist
                results_dict['AlleleY'] = alleleYlist
                results_dict['SampleName'] = samplenamelist

                results_dict['Call']  = calllist
                results_dict['Confidence'] = callconfidencelist
                results_dict['FinalCall'] = callfinallist
                results_dict['XIntensity'] = xintensitylist
                results_dict['YIntensity'] = yintensitylist
                results_dict['TotalFailedAssays'] = totalassayfails
                if totalassayfails > failThreshold:
                    status = 'ASSAYFAIL'
                else:
                    status = 'ASSAYPASS'
                results_dict['Status'] = status

                jsonResultsString = json.dumps(results_dict)
                return_values_dict[sampleindex] = jsonResultsString
                #print sampleindex

            return return_values_dict
        except Exception as e:
            print e
            raise e

    @classmethod
    def main(cls, args):

        try:
            fileName = "/Users/s0199669/cgsdev/gims/files/FluidigmSampleDetails.xlsx"
            os.path.isfile(fileName);
            os.path.exists(fileName);
            qubitResultsParser = FluidigmResultsParser()
            return_dict = qubitResultsParser.parseResults(fileName)
            for index in return_dict:
                jsonstring = return_dict.get(index)
                #print index, jsonstring


        except Exception as e:
            print(e)
            exit(1)

if __name__ == '__main__':
    import sys
    FluidigmResultsParser.main(sys.argv)