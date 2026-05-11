from django.conf import settings
from api.services.client import PayonusClient


def fetch_banks(currency=None):

    params = {}

    if currency:
        params["key"] = currency

    response = PayonusClient.get("/api/v1/banks", params=params)

    return response


def perform_name_enquiry(data):

    payload = {
        "institutionCode": data["institution_code"],
        "accountNumber": data["account_number"],
        "businessId": (settings.PAYONUS_BUSINESS_ID),
        "currency": data.get("currency", "NGN"),
    }

    response = PayonusClient.post("/api/v1/transfer-requests/name-enquiry", payload)

    return response
