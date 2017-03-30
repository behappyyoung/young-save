from django.test import TestCase, LiveServerTestCase
from mybackend import LoadOntology
from datetime import datetime
from django.core.cache import cache, caches


class TestLoadOntology(TestCase):
    def test_LoadOntology(self):

        l = LoadOntology.LoadOntology()
        unsorted = l.getSortedDiseaseList([93,100,969,1319,2133,2151,11968,100704], None)

        sortedList = sorted(unsorted, key=lambda x: x[1], reverse=True)
        print ('unsorted', unsorted[:5])
        print ('sorted', sortedList[:5])
        self.assertEqual(len(unsorted), len(sortedList))


class TestMemcached(TestCase):
    def test_memcached(self):
        print (datetime.now())
        l = LoadOntology.LoadOntology()

        print (datetime.now())
        memcache = caches['memcached']
        memcache2 = caches['memcached']
        self.assertEqual(memcache, memcache2)
        memcache.set('ontology', l)

        lc = memcache.get('ontology')
        print('oncology from memcached cache')
        print (datetime.now())
        self.assertEqual(type(l), type(lc))


class TestFileCache(TestCase):
    def test_filecache(self):
        print (datetime.now())
        l = LoadOntology.LoadOntology()

        print (datetime.now())

        cache.set('ontology', l)

        lc = cache.get('ontology')
        print('oncology from cache')
        print (datetime.now())
        print (type(l))
        self.assertEqual(type(l), type(lc))
        # self.assertSequenceEqual(l, lc)