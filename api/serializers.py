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
