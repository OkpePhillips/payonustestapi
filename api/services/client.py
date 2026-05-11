import requests

from django.conf import settings

from .auth import get_access_token


class PayonusClient:

    @staticmethod
    def headers():
        return {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @staticmethod
    def get(endpoint, params=None):

        url = f"{settings.PAYONUS_BASE_URL}{endpoint}"

        response = requests.get(url, headers=PayonusClient.headers(), params=params)

        response.raise_for_status()

        return response.json()

    @staticmethod
    def post(endpoint, payload=None):

        url = f"{settings.PAYONUS_BASE_URL}{endpoint}"

        response = requests.post(url, headers=PayonusClient.headers(), json=payload)

        response.raise_for_status()

        return response.json()
