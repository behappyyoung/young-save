from django.test import TestCase, LiveServerTestCase
from mybackend.models import CustomSQL, CustomSql
from tracker.models import Samples
from mybackend  import functions


class CustomSQLTest(TestCase):
    def test_CustomSQL(self):
        print('\n Testing CustomSQL')
        CC = CustomSQL()
        QS = CC.my_custom_sql('Select * from users_userprofile')
        # print(CC, QS, type(QS), len(QS))
        self.assertEqual(isinstance(CC, CustomSQL), True)
        QS = CC.my_custom_sql('Select * from tracker_samples')
        # print(CC, QS, type(QS), len(QS))


class CustomSqlTest(LiveServerTestCase):
    def test_CustomSql(self):
        print('\n Testing CustomSql')
        cc = CustomSql()
        qs = cc.custom_sql('Select * from users_userprofile')
        # print(cc, qs, type(qs), len(qs))
        self.assertEqual(isinstance(cc, CustomSql), True)
        qs = cc.custom_sql('Select * from tracker_samples')
        # print(cc, qs, type(qs), len(qs))
        queryset = Samples.objects.all()
        # print(queryset, type(queryset), len(queryset), queryset.__dict__)


class FunctionsTest(TestCase):
    def test_functions(self):
        print ('\n Testing mybackend functions')
        getDiv = functions.getPulseDiv()
        self.assertEqual(type(getDiv).__name__, 'str')
        getDiv = functions.getMednewsDiv()
        self.assertEqual(type(getDiv).__name__, 'str')
        terms = functions.getTermsAll()
        self.assertEqual(type(terms).__name__, 'list')
