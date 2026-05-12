from api.models import Transaction, WebhookLog


def normalize_status(status):
    if not status:
        return "processing"

    status = status.lower()

    status_map = {
        "successful": "successful",
        "success": "successful",
        "completed": "successful",
        "failed": "failed",
        "failure": "failed",
        "rejected": "rejected",
        "pending": "pending",
        "processing": "processing",
    }

    return status_map.get(status, "processing")


def extract_webhook_data(payload):
    data = payload.get("data", payload)

    onus_reference = data.get("onusReference") or payload.get("onusReference")

    merchant_reference = (
        data.get("merchantReference")
        or data.get("reference")
        or payload.get("merchantReference")
        or payload.get("reference")
    )

    payment_status = (
        data.get("paymentStatus")
        or data.get("status")
        or payload.get("paymentStatus")
        or payload.get("status")
    )

    event_type = payload.get("eventType") or payload.get("event") or payload.get("type")

    return {
        "data": data,
        "onus_reference": onus_reference,
        "merchant_reference": merchant_reference,
        "payment_status": payment_status,
        "event_type": event_type,
    }


def process_payonus_webhook(payload, signature=None):
    extracted = extract_webhook_data(payload)

    webhook_log = WebhookLog.objects.create(
        event_type=extracted["event_type"],
        onus_reference=extracted["onus_reference"],
        merchant_reference=extracted["merchant_reference"],
        payload=payload,
        signature=signature,
    )

    transaction = None

    if extracted["onus_reference"]:
        transaction = Transaction.objects.filter(
            provider_reference=extracted["onus_reference"]
        ).first()

        if not transaction:
            transaction = Transaction.objects.filter(
                onus_reference=extracted["onus_reference"]
            ).first()

    if not transaction and extracted["merchant_reference"]:
        transaction = Transaction.objects.filter(
            reference=extracted["merchant_reference"]
        ).first()

    if not transaction:
        webhook_log.processing_note = "No matching transaction found"
        webhook_log.processed = False
        webhook_log.save()

        return {
            "processed": False,
            "message": "Webhook received but no matching transaction found",
            "webhook_id": webhook_log.id,
        }

    transaction.status = normalize_status(extracted["payment_status"])

    transaction.provider_response = payload

    if extracted["onus_reference"]:
        transaction.provider_reference = extracted["onus_reference"]
        transaction.onus_reference = extracted["onus_reference"]

    transaction.save()

    webhook_log.processed = True
    webhook_log.processing_note = "Transaction updated successfully"
    webhook_log.save()

    return {
        "processed": True,
        "message": "Webhook processed successfully",
        "transaction_reference": str(transaction.reference),
        "status": transaction.status,
        "webhook_id": webhook_log.id,
    }
