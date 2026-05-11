from django.contrib import admin

from .models import (
    Customer,
    CustomerAddress,
    Transaction,
    VirtualAccount,
    MobileMoneyPayment,
    Beneficiary,
    Payout,
    BulkTransfer,
    BulkTransferItem,
    Wallet,
    WalletTransaction,
    WebhookLog,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone",
    )


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "city",
        "state",
        "country_code",
    )

    search_fields = (
        "customer__name",
        "customer__email",
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reference",
        "onus_reference",
        "tx_type",
        "channel",
        "amount",
        "currency",
        "status",
        "created_at",
    )

    list_filter = (
        "tx_type",
        "channel",
        "status",
        "currency",
    )

    search_fields = (
        "reference",
        "onus_reference",
    )


@admin.register(VirtualAccount)
class VirtualAccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "account_type",
        "account_number",
        "bank_name",
        "active",
    )

    list_filter = (
        "account_type",
        "active",
    )

    search_fields = (
        "account_number",
        "account_name",
    )


@admin.register(MobileMoneyPayment)
class MobileMoneyPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mobile_number",
        "network",
        "otp_required",
        "otp_verified",
        "payment_status",
    )

    list_filter = (
        "network",
        "otp_required",
        "otp_verified",
        "payment_status",
    )

    search_fields = (
        "mobile_number",
        "transaction__reference",
    )


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "account_number",
        "bank_name",
        "currency",
        "country_code",
    )

    search_fields = (
        "name",
        "account_number",
    )


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "transaction",
        "transfer_type",
        "fee",
        "payment_status",
    )

    list_filter = (
        "transfer_type",
        "payment_status",
    )

    search_fields = (
        "transaction__reference",
        "transaction__onus_reference",
    )


class BulkTransferItemInline(admin.TabularInline):
    model = BulkTransferItem
    extra = 0


@admin.register(BulkTransfer)
class BulkTransferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reference",
        "transfer_type",
        "currency",
        "status",
        "created_at",
    )

    list_filter = (
        "transfer_type",
        "currency",
        "status",
    )

    search_fields = ("reference",)

    inlines = [BulkTransferItemInline]


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet_name",
        "currency",
        "available_balance",
        "status",
        "active",
    )

    list_filter = (
        "currency",
        "status",
        "active",
    )

    search_fields = (
        "wallet_name",
        "business_name",
    )


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "onus_reference",
        "product",
        "channel",
        "transaction_type",
        "transaction_status",
        "amount",
    )

    list_filter = (
        "product",
        "channel",
        "transaction_type",
        "transaction_status",
    )

    search_fields = ("onus_reference",)


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event_type",
        "processed",
        "created_at",
    )

    list_filter = ("processed",)

    search_fields = ("event_type",)
