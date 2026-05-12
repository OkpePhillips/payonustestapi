from django.conf import settings
from api.models import Transaction
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


def initiate_bank_transfer(data):

    transaction = Transaction.objects.create(
        tx_type="payout",
        channel="bank_transfer",
        amount=data["amount"],
        currency=data["currency"],
        country_code=data["country_code"],
        status="pending",
    )

    payload = {
        "reference": str(transaction.reference),
        "amount": float(data["amount"]),
        "beneficiaryAccountNumber": data["beneficiary_account_number"],
        "beneficiaryAccountName": data["beneficiary_account_name"],
        "beneficiaryBankCode": data["beneficiary_bank_code"],
        "transferType": data["transfer_type"],
        "countryCode": data["country_code"],
        "currency": data["currency"],
        "businessId": (settings.PAYONUS_BUSINESS_ID),
        "email": data["email"],
    }

    if data.get("narration"):

        payload["narration"] = data["narration"]

    if data.get("notification_url"):

        payload["notificationUrl"] = data["notification_url"]

    response = PayonusClient.post("/api/v1/transfer-requests/bank-transfer", payload)

    response_data = response.get("data", response)

    transaction.provider_response = response

    transaction.onus_reference = response_data.get("onusReference")

    transaction.fee = response_data.get("fee", 0)

    transaction.status = response_data.get("paymentStatus", "pending").lower()

    transaction.save()

    return response


def initiate_mobile_money_payout(data):
    transaction = Transaction.objects.create(
        tx_type="payout",
        channel="mobile_money_payout",
        amount=data["amount"],
        currency=data["currency"],
        country_code=data["country_code"],
        status="pending",
    )

    payload = {
        "beneficiaryAccountNumber": data["beneficiary_account_number"],
        "beneficiaryAccountName": data["beneficiary_account_name"],
        "momoNetwork": data["momo_network"],
        "transferType": "WALLET_TO_MOMO",
        "amount": str(data["amount"]),
        "businessId": settings.PAYONUS_BUSINESS_ID,
        "reference": str(transaction.reference),
        "countryCode": data["country_code"],
        "currency": data["currency"],
    }

    if data.get("narration"):
        payload["narration"] = data["narration"]

    if data.get("notification_url"):
        payload["notificationUrl"] = data["notification_url"]

    response = PayonusClient.post("/api/v1/transfer-requests/bank-transfer", payload)

    response_data = response.get("data", response)

    transaction.provider_response = response
    transaction.onus_reference = response_data.get("onusReference")
    transaction.fee = response_data.get("fee", 0)
    transaction.status = response_data.get("paymentStatus", "pending").lower()
    transaction.save()

    return response


def initiate_eft_payout(data):
    transaction = Transaction.objects.create(
        tx_type="payout",
        channel="eft_payout",
        amount=data["amount"],
        currency=data["currency"],
        country_code=data["country_code"],
        status="pending",
    )

    payload = {
        "beneficiaryAccountNumber": data["beneficiary_account_number"],
        "beneficiaryAccountName": data["beneficiary_account_name"],
        "eftBank": data["eft_bank"],
        "transferType": "WALLET_TO_EFT",
        "amount": str(data["amount"]),
        "businessId": settings.PAYONUS_BUSINESS_ID,
        "reference": str(transaction.reference),
        "countryCode": data["country_code"],
        "currency": data["currency"],
    }

    if data.get("narration"):
        payload["narration"] = data["narration"]

    if data.get("notification_url"):
        payload["notificationUrl"] = data["notification_url"]

    response = PayonusClient.post("/api/v1/transfer-requests/bank-transfer", payload)

    response_data = response.get("data", response)

    transaction.provider_response = response
    transaction.onus_reference = response_data.get("onusReference")
    transaction.fee = response_data.get("fee", 0)
    transaction.status = response_data.get("paymentStatus", "pending").lower()
    transaction.save()

    return response
