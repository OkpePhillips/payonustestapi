from django.conf import settings

from api.models import (
    Customer,
    CustomerAddress,
    Transaction,
    VirtualAccount,
)

from .client import PayonusClient


def create_dynamic_virtual_account(data):

    customer_data = data["customer"]

    address_data = customer_data.pop("address", None)

    customer, _ = Customer.objects.get_or_create(
        email=customer_data["email"], defaults=customer_data
    )

    # update existing customer
    for key, value in customer_data.items():
        setattr(customer, key, value)

    customer.save()

    # update/create address
    if address_data:
        CustomerAddress.objects.update_or_create(
            customer=customer, defaults=address_data
        )

    transaction = Transaction.objects.create(
        customer=customer,
        tx_type="payin",
        channel="dynamic_virtual_account",
        amount=data["amount"],
        currency="NGN",
        country_code="NG",
        status="pending",
    )

    payload = {
        "amount": float(data["amount"]),
        "reference": str(transaction.reference),
        "businessId": settings.PAYONUS_BUSINESS_ID,
        "customer": {
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "externalId": customer.external_id or str(customer.id),
        },
    }

    if data.get("wallet_type"):
        payload["walletType"] = data["wallet_type"]

    if data.get("payment_channel"):
        payload["paymentChannel"] = data["payment_channel"]

    if data.get("redirect_url"):
        payload["redirectUrl"] = data["redirect_url"]

    # wallet payment option
    # if data.get("payment_channel") == "PAY_WITH_WALLET":

    #     payload["walletType"] = data.get("wallet_type")

    #     payload["paymentChannel"] = "PAY_WITH_WALLET"

    #     payload["redirectUrl"] = data.get("redirect_url")

    response = PayonusClient.post("/api/v1/virtual-accounts/dynamic", payload)

    response_data = response.get("data", {})

    transaction.onus_reference = response_data.get("onusReference")

    transaction.provider_response = response

    transaction.status = "processing"

    transaction.save()

    virtual_account = VirtualAccount.objects.create(
        transaction=transaction,
        customer=customer,
        account_type=(
            "wallet" if data.get("payment_channel") == "PAY_WITH_WALLET" else "dynamic"
        ),
        account_name=response_data.get("accountName"),
        account_number=response_data.get("accountNumber"),
        bank_name=response_data.get("bankName"),
        completion_url=response_data.get("completionUrl"),
        metadata=response,
    )

    return virtual_account


def create_fixed_virtual_account(data):

    customer_data = data["customer"]

    address_data = customer_data.pop("address", None)

    customer, _ = Customer.objects.get_or_create(
        email=customer_data["email"], defaults=customer_data
    )

    for key, value in customer_data.items():
        setattr(customer, key, value)

    customer.save()

    if address_data:

        CustomerAddress.objects.update_or_create(
            customer=customer, defaults=address_data
        )

    transaction = Transaction.objects.create(
        customer=customer,
        tx_type="payin",
        channel="fixed_virtual_account",
        amount=0,
        currency="NGN",
        country_code="NG",
        status="processing",
    )

    print(customer.dob)

    payload = {
        "customer": {
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "externalId": customer.external_id,
            "bvn": customer.bvn,
            "address": {
                "line1": address_data.get("line1"),
                "line2": address_data.get("line2"),
                "city": address_data.get("city"),
                "state": address_data.get("state"),
                "postalCode": address_data.get("postal_code"),
                "countryCode": address_data.get("country_code"),
            },
        },
        "dob": (customer.dob.strftime("%Y-%m-%d")),
        "businessId": (settings.PAYONUS_BUSINESS_ID),
        "reference": str(transaction.reference),
    }

    if data.get("notification_url"):

        payload["notificationUrl"] = data["notification_url"]

    if data.get("narration"):

        payload["narration"] = data["narration"]

    response = PayonusClient.post("/api/v1/virtual-accounts/fixed-account", payload)

    response_data = response.get("data", {})
    print(response_data)

    transaction.provider_response = response

    transaction.save()

    virtual_account = VirtualAccount.objects.create(
        transaction=transaction,
        customer=customer,
        account_type="fixed",
        account_name=response_data.get("accountName"),
        account_number=response_data.get("accountNumber"),
        bank_name=response_data.get("bankName"),
        metadata=response,
    )

    return virtual_account
