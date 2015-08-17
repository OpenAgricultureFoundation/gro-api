from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class RestartTestCase(APITestCase):
    def test_restart(self):
        url = reverse('restart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
