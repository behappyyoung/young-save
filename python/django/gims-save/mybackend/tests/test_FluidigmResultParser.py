from django.test import TestCase
from mybackend import FluidigmResultsParser


class TestLoadOntology(TestCase):
    def test_FluidigmResultsParser(self):

        fparser = FluidigmResultsParser.FluidigmResultsParser()
        filename = "/Users/s0199669/cgsdev/gims/files/FluidigmSampleDetails.xlsx"
        re = fparser.parseResults(filename)
        print type(re)

        # self.assertEqual(len(unsorted), len(sortedList))

