from django.db import models
import uuid


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# =========================
# CUSTOMERS
# =========================
class Customer(TimeStampedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30)

    external_id = models.CharField(max_length=120, blank=True, null=True)

    nin = models.CharField(max_length=20, blank=True, null=True)

    bvn = models.CharField(max_length=20, blank=True, null=True)

    dob = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class CustomerAddress(TimeStampedModel):
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name="address"
    )

    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True, null=True)

    city = models.CharField(max_length=100, blank=True, null=True)

    state = models.CharField(max_length=100, blank=True, null=True)

    postal_code = models.CharField(max_length=20, blank=True, null=True)

    country_code = models.CharField(max_length=2, default="NG")

    def __str__(self):
        return f"{self.customer.name} Address"


# =========================
# TRANSACTIONS
# =========================
class Transaction(TimeStampedModel):
    TYPE_CHOICES = (
        ("payin", "Payin"),
        ("payout", "Payout"),
    )

    CHANNEL_CHOICES = (
        ("dynamic_virtual_account", "Dynamic Virtual Account"),
        ("fixed_virtual_account", "Fixed Virtual Account"),
        ("wallet_link", "Wallet Link"),
        ("mobile_money_collection", "Mobile Money Collection"),
        ("bank_transfer", "Bank Transfer"),
        ("mobile_money_payout", "Mobile Money Payout"),
        ("eft_payout", "EFT Payout"),
        ("wallet_transfer", "Wallet Transfer"),
        ("bulk_transfer", "Bulk Transfer"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("successful", "Successful"),
        ("failed", "Failed"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    onus_reference = models.CharField(max_length=120, blank=True, null=True)

    tx_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    channel = models.CharField(max_length=50, choices=CHANNEL_CHOICES)

    amount = models.DecimalField(max_digits=15, decimal_places=2)

    currency = models.CharField(max_length=10, default="NGN")

    country_code = models.CharField(max_length=5, default="NG")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    provider_response = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return str(self.reference)


# =========================
# PAYMENTS
# =========================
class VirtualAccount(TimeStampedModel):
    ACCOUNT_TYPES = (
        ("dynamic", "Dynamic"),
        ("fixed", "Fixed"),
        ("wallet", "Wallet"),
    )

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="virtual_account",
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="virtual_accounts"
    )

    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)

    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=255)
    onus_reference = models.CharField(max_length=255)

    completion_url = models.URLField(max_length=2000, blank=True, null=True)

    active = models.BooleanField(default=True)

    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.account_number} - {self.bank_name}"


class MobileMoneyPayment(TimeStampedModel):
    transaction = models.OneToOneField(
        Transaction, on_delete=models.CASCADE, related_name="mobile_money"
    )

    network = models.CharField(max_length=100)

    mobile_number = models.CharField(max_length=30)

    otp_required = models.BooleanField(default=False)

    otp_verified = models.BooleanField(default=False)

    initiating_code = models.CharField(max_length=100, blank=True, null=True)

    payment_status = models.CharField(max_length=50, default="PROCESSING")

    def __str__(self):
        return self.mobile_number


# =========================
# PAYOUTS
# =========================
class Beneficiary(TimeStampedModel):
    name = models.CharField(max_length=255)

    email = models.EmailField(blank=True, null=True)

    phone = models.CharField(max_length=30, blank=True, null=True)

    account_number = models.CharField(max_length=50)

    bank_code = models.CharField(max_length=50, blank=True, null=True)

    bank_name = models.CharField(max_length=255, blank=True, null=True)

    country_code = models.CharField(max_length=5, default="NG")

    currency = models.CharField(max_length=10, default="NGN")

    momo_network = models.CharField(max_length=100, blank=True, null=True)

    eft_bank = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Payout(TimeStampedModel):
    TRANSFER_TYPES = (
        ("WALLET_TO_BANK_ACCOUNT", "Wallet to Bank"),
        ("WALLET_TO_WALLET", "Wallet to Wallet"),
        ("WALLET_TO_MOMO", "Wallet to MoMo"),
        ("WALLET_TO_EFT", "Wallet to EFT"),
    )

    transaction = models.OneToOneField(
        Transaction, on_delete=models.CASCADE, related_name="payout"
    )

    beneficiary = models.ForeignKey(
        Beneficiary, on_delete=models.SET_NULL, null=True, blank=True
    )

    transfer_type = models.CharField(max_length=50, choices=TRANSFER_TYPES)

    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    payment_status = models.CharField(max_length=50, default="PENDING")

    notification_url = models.URLField(blank=True, null=True)

    narration = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.transaction.reference)


class BulkTransfer(TimeStampedModel):
    reference = models.CharField(max_length=120, unique=True)

    business_id = models.CharField(max_length=120)

    transfer_type = models.CharField(max_length=50)

    country_code = models.CharField(max_length=5)

    currency = models.CharField(max_length=10)

    description = models.TextField(blank=True, null=True)

    notification_url = models.URLField(blank=True, null=True)

    momo_network = models.CharField(max_length=100, blank=True, null=True)

    csv_file = models.FileField(upload_to="bulk_transfers/")

    status = models.CharField(max_length=50, default="pending")

    response_payload = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.reference


class BulkTransferItem(TimeStampedModel):
    bulk_transfer = models.ForeignKey(
        BulkTransfer, on_delete=models.CASCADE, related_name="items"
    )

    beneficiary_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    bank_code = models.CharField(max_length=50)

    amount = models.DecimalField(max_digits=15, decimal_places=2)

    email = models.EmailField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=50, default="pending")

    def __str__(self):
        return self.beneficiary_name


# =========================
# WALLETS
# =========================
class Wallet(TimeStampedModel):
    wallet_id = models.CharField(max_length=120, unique=True)

    business_id = models.CharField(max_length=120)

    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=50)

    available_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    lien_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    purpose = models.CharField(max_length=100, blank=True, null=True)

    wallet_name = models.CharField(max_length=255)

    business_name = models.CharField(max_length=255)

    merchant_name = models.CharField(max_length=255)

    aggregator_wallet = models.BooleanField(default=False)

    payout_allowed = models.BooleanField(default=True)

    active = models.BooleanField(default=True)

    raw_response = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.wallet_name} ({self.currency})"


class WalletTransaction(TimeStampedModel):
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )

    transaction = models.ForeignKey(
        Transaction, on_delete=models.SET_NULL, null=True, blank=True
    )

    product = models.CharField(max_length=50)
    channel = models.CharField(max_length=50)
    transaction_type = models.CharField(max_length=50)
    transaction_status = models.CharField(max_length=50)

    amount = models.DecimalField(max_digits=20, decimal_places=2)

    onus_reference = models.CharField(max_length=120)

    narration = models.TextField(blank=True, null=True)

    reversal = models.BooleanField(default=False)
    fee = models.BooleanField(default=False)

    raw_response = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.onus_reference


# =========================
# WEBHOOKS
# =========================
class WebhookLog(TimeStampedModel):
    event_type = models.CharField(max_length=100, blank=True, null=True)

    payload = models.JSONField(default=dict)
    signature = models.TextField()

    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Webhook {self.id}"
