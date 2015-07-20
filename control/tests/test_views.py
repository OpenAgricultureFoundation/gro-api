from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class RestartTestCase(APITestCase):
    def test_restart(self):
        url = reverse('restart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for i in range(3):
            command_response = response.data[i]
            self.assertEqual(command_response['returncode'], 0)
