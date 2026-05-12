from rest_framework import serializers

from .models import (
    Customer,
    CustomerAddress,
    Transaction,
    VirtualAccount,
)


class CustomerAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerAddress

        fields = [
            "line1",
            "line2",
            "city",
            "state",
            "postal_code",
            "country_code",
        ]


class CustomerSerializer(serializers.ModelSerializer):

    address = CustomerAddressSerializer(required=False)

    class Meta:
        model = Customer

        fields = [
            "name",
            "email",
            "phone",
            "external_id",
            "nin",
            "bvn",
            "dob",
            "address",
        ]


class DynamicVirtualAccountSerializer(serializers.Serializer):

    amount = serializers.DecimalField(max_digits=15, decimal_places=2)

    customer = CustomerSerializer()

    payment_channel = serializers.CharField(required=False, default="BANK_TRANSFER")

    wallet_type = serializers.CharField(required=False)

    redirect_url = serializers.URLField(required=False)

    wallet_type = serializers.ChoiceField(choices=["OPAY", "PALMPAY"], required=False)

    payment_channel = serializers.CharField(required=False)

    redirect_url = serializers.URLField(required=False)


class VirtualAccountResponseSerializer(serializers.ModelSerializer):

    transaction_reference = serializers.CharField(source="transaction.reference")

    class Meta:
        model = VirtualAccount

        fields = fields = "__all__"

class FixedVirtualAccountSerializer(serializers.Serializer):

    customer = CustomerSerializer()

    narration = serializers.CharField(required=False)

    notification_url = serializers.URLField(required=False)


class MobileMoneyCollectionSerializer(serializers.Serializer):

    customer = CustomerSerializer()

    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    narration = serializers.CharField()

    momo_network = serializers.CharField()

    initiating_code = serializers.CharField(required=False, allow_blank=True)


class VerifyMobileMoneyOTPSerializer(serializers.Serializer):

    onus_reference = serializers.CharField()

    otp = serializers.CharField()


class NameEnquirySerializer(serializers.Serializer):

    institution_code = serializers.CharField()

    account_number = serializers.CharField()

    currency = serializers.CharField(required=False, default="NGN")


class BankTransferSerializer(serializers.Serializer):

    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    beneficiary_account_number = serializers.CharField()

    beneficiary_account_name = serializers.CharField()

    beneficiary_bank_code = serializers.CharField()

    currency = serializers.CharField(default="NGN")

    country_code = serializers.CharField(default="NG")

    email = serializers.EmailField()

    narration = serializers.CharField(required=False, allow_blank=True)

    notification_url = serializers.URLField(required=False)

    transfer_type = serializers.CharField(default="WALLET_TO_BANK_ACCOUNT")


class FundSandboxWalletSerializer(serializers.Serializer):

    account_number = serializers.CharField()

    amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class MobileMoneyPayoutSerializer(serializers.Serializer):
    beneficiary_account_number = serializers.CharField()
    beneficiary_account_name = serializers.CharField()
    momo_network = serializers.CharField()

    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    country_code = serializers.CharField(default="CI")
    currency = serializers.CharField(default="XOF")

    narration = serializers.CharField(required=False, allow_blank=True)

    notification_url = serializers.URLField(required=False)


class EFTPayoutSerializer(serializers.Serializer):
    beneficiary_account_number = serializers.CharField()
    beneficiary_account_name = serializers.CharField()
    eft_bank = serializers.CharField()

    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    country_code = serializers.CharField(default="ZA")
    currency = serializers.CharField(default="ZAR")

    narration = serializers.CharField(required=False, allow_blank=True)

    notification_url = serializers.URLField(required=False)


class WalletTransferSerializer(serializers.Serializer):
    beneficiary_business_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    country_code = serializers.CharField(default="NG")
    currency = serializers.CharField(default="NGN")
    narration = serializers.CharField(default="Wallet transfer")


class VerifySinglePaymentSerializer(serializers.Serializer):
    onus_reference = serializers.CharField()


class BulkTransferSerializer(serializers.Serializer):
    file = serializers.FileField()
    description = serializers.CharField(required=False, allow_blank=True)
    transfer_type = serializers.CharField(default="WALLET_TO_BANK_ACCOUNT")
    country_code = serializers.CharField(default="NG")
    currency = serializers.CharField(default="NGN")
    notification_url = serializers.URLField(required=False, allow_blank=True)
    momo_network = serializers.CharField(required=False, allow_blank=True)
