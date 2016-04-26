import django

from django.test import TestCase

from .models import TestModel


class SampleTestCase(TestCase):

    def test_simple(self):
        one = TestModel.objects.create(
            foo='testing',
            bar=420,
            baz={'foo': 'fighters'}
        )

        one = TestModel.objects.get()
        self.assertTrue(one.id is not None)
        if django.VERSION[1] >= 9:
            self.assertIsInstance(one.baz, dict)
