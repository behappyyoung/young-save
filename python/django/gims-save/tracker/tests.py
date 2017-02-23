from django.test import TestCase
from tracker.models import OrderStatus, Samples


# Create your tests here.
class SamplesModelTest(TestCase):
    def test_pass_string_representation(self):
        pass

    def test_Samples(self):
        s = Samples.objects.all()
        self.assertEqual(len(s), 0)
        self.assertSequenceEqual(s, [])


class OrderStatusTest(TestCase):
    def setUp(self):
        OrderStatus.objects.create(status_name='TEST',status='Testing')

    def test_orderstatus(self):
        os = OrderStatus.objects.all()
        self.assertEqual(len(os), 1)


class TrackerViewsTestCase(TestCase):
    def test_orders(self):
        response = self.client.get('/orders/')
        self.assertRedirects(response, '/saml/?next=/orders/', 302)
