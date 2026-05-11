import time
import requests

from django.conf import settings

TOKEN_CACHE = {"token": None, "expires_at": 0}


def get_access_token():
    """
    Generate and cache Payonus access token.
    """

    current_time = time.time()

    # Return cached token if still valid
    if TOKEN_CACHE["token"] and TOKEN_CACHE["expires_at"] > current_time:
        return TOKEN_CACHE["token"]

    url = f"{settings.PAYONUS_BASE_URL}/api/v1/access-token"

    payload = {
        "apiClientId": settings.PAYONUS_CLIENT_ID,
        "apiClientSecret": settings.PAYONUS_CLIENT_SECRET,
    }

    response = requests.post(url, json=payload)

    response.raise_for_status()

    data = response.json()

    access_token = data["data"].get("access_token")

    expires_in = data["data"].get("expires_in", 3600)

    # cache slightly before expiry
    TOKEN_CACHE["token"] = access_token
    TOKEN_CACHE["expires_at"] = current_time + expires_in - 60

    print(access_token)

    return access_token
