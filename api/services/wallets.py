from django.conf import settings
from api.models import Transaction
from api.services.client import PayonusClient

def fetch_wallets():
    return PayonusClient.get(
        f"/api/v1/merchants/{settings.PAYONUS_MERCHANT_ID}/wallets"
    )


def wallet_to_wallet_transfer(data):
    transaction = Transaction.objects.create(
        tx_type="payout",
        channel="wallet_transfer",
        amount=data["amount"],
        currency=data["currency"],
        country_code=data["country_code"],
        status="pending",
    )

    payload = {
        "reference": str(transaction.reference),
        "amount": float(data["amount"]),
        "senderBusinessId": settings.PAYONUS_BUSINESS_ID,
        "beneficiaryBusinessId": data["beneficiary_business_id"],
        "countryCode": data["country_code"],
        "currency": data["currency"],
        "narration": data["narration"],
    }

    response = PayonusClient.post("/api/v1/transfer-requests/wallet-transfer", payload)

    response_data = response.get("data", response)

    transaction.provider_response = response
    transaction.provider_reference = response_data.get("onusReference")
    transaction.fee = response_data.get("fee", 0)
    transaction.status = response_data.get("paymentStatus", "pending").lower()
    transaction.save()

    return response


def fetch_wallet_transactions(params=None):
    params = params or {}
    params["businessId"] = settings.PAYONUS_BUSINESS_ID

    return PayonusClient.get(
        f"/api/v1/merchants/{settings.PAYONUS_MERCHANT_ID}/wallet-transactions",
        params=params,
    )
