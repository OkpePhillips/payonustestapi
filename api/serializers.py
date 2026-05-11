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
    reference = serializers.CharField()
    businessId = serializers.CharField()


class VirtualAccountResponseSerializer(serializers.ModelSerializer):

    transaction_reference = serializers.CharField(source="transaction.reference")

    class Meta:
        model = VirtualAccount

        fields = [
            "id",
            "account_type",
            "account_name",
            "account_number",
            "bank_name",
            "completion_url",
            "transaction_reference",
            "created_at",
        ]


class FixedVirtualAccountSerializer(serializers.Serializer):

    customer = CustomerSerializer()

    reference = serializers.CharField(required=False)

    narration = serializers.CharField(required=False)

    notification_url = serializers.URLField(required=False)
