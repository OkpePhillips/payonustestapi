import requests

from django.conf import settings

from .auth import get_access_token


class PayonusClient:

    @staticmethod
    def headers():
        token = get_access_token()

        if not token:
            raise ValueError("Payonus access token is missing")

        return {
            "Authorization": f"Bearer {token}",
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
