from django.test import TestCase, LiveServerTestCase
from gims import settings
from django.contrib.auth import authenticate, login,logout

# from django.test import Client
# from django.core.urlresolvers import reverse
# client = Client()
# response = client.get(reverse('mybackend'))
# print response.status_code


class TestCalls(TestCase):
    def test_call_view_denies_anonymous(self):
        response = self.client.get('/mybackend/', follow=True)
        self.assertRedirects(response, '/saml/?next=/mybackend/')

    def test_login(self):
        # response = self.client.get('/login/manager/', follow=True)
        # print settings.TESTING, response
        # self.assertRedirects(response.status_code, 200)
        user = authenticate(username='manager', password='saml')
        # request.session['username'] = 'manager'
        response = self.client.get('/mybackend/', follow=True)
        self.assertRedirects(response, '/saml/?next=/mybackend/')

        #

    def test_get_samplefiles(self):
        response = self.client.post('/mybackend/get_samplefiles/', {'sid': 9})
        print response
        self.assertEqual(response.status_code, 200)