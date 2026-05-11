from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

from drf_yasg.utils import swagger_auto_schema
from .models import WebhookLog
from .serializers import (
    DynamicVirtualAccountSerializer,
    MobileMoneyCollectionSerializer,
    VerifyMobileMoneyOTPSerializer,
    VirtualAccountResponseSerializer,
    FixedVirtualAccountSerializer,
)

from .services.payments import (
    create_dynamic_virtual_account,
    create_fixed_virtual_account,
    fetch_banks,
    fetch_mobile_money_networks,
    initiate_mobile_money_collection,
    list_fixed_virtual_accounts,
    verify_mobile_money_otp,
)


class CreateDynamicVirtualAccountView(APIView):

    @swagger_auto_schema(
        request_body=DynamicVirtualAccountSerializer,
        responses={201: VirtualAccountResponseSerializer},
        operation_summary=("Create Dynamic Virtual Account"),
        operation_description=(
            "Creates a Payonus dynamic virtual " "account for payment collection."
        ),
    )
    def post(self, request):

        serializer = DynamicVirtualAccountSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        virtual_account = create_dynamic_virtual_account(serializer.validated_data)

        response_serializer = VirtualAccountResponseSerializer(virtual_account)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CreateFixedVirtualAccountView(APIView):

    @swagger_auto_schema(
        request_body=(FixedVirtualAccountSerializer),
        responses={201: (VirtualAccountResponseSerializer)},
        operation_summary=("Create Fixed Virtual Account"),
        operation_description=(
            "Creates a fixed virtual account " "for recurring collections."
        ),
    )
    def post(self, request):

        serializer = FixedVirtualAccountSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        virtual_account = create_fixed_virtual_account(serializer.validated_data)

        response_serializer = VirtualAccountResponseSerializer(virtual_account)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@permission_classes([AllowAny])
class PayonusWebhookView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        payload = request.data

        WebhookLog.objects.create(
            event_type=payload.get("eventType"),
            payload=payload,
            signature=request.headers.get("X-Webhook-Signature", ""),
            processed=True,
        )

        return Response({"success": True, "message": "Webhook received"}, status=200)


class FixedVirtualAccountListView(APIView):

    def get(self, request):

        params = {}

        account_number = request.query_params.get("accountNumber")

        business_ids = request.query_params.get("businessIds")

        created_from = request.query_params.get("createdFrom")

        created_to = request.query_params.get("createdTo")

        if account_number:
            params["accountNumber"] = account_number

        if business_ids:
            params["businessIds"] = business_ids

        if created_from:
            params["createdFrom"] = created_from

        if created_to:
            params["createdTo"] = created_to

        response = list_fixed_virtual_accounts(params=params)

        return Response(response)


class MobileMoneyCollectionView(APIView):

    @swagger_auto_schema(
        request_body=(MobileMoneyCollectionSerializer),
        responses={201: (MobileMoneyCollectionSerializer)},
        operation_summary=("Mobile money payment collection"),
        operation_description=("Collect money using mobile money."),
    )
    def post(self, request):

        serializer = MobileMoneyCollectionSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        response = initiate_mobile_money_collection(serializer.validated_data)

        return Response(response)


class VerifyMobileMoneyOTPView(APIView):

    @swagger_auto_schema(
        request_body=(VerifyMobileMoneyOTPSerializer),
        responses={201: (VerifyMobileMoneyOTPSerializer)},
        operation_summary=("Mobile money payment otp verification"),
        operation_description=("Verify otp for mobile money payment."),
    )

    def post(self, request):

        serializer = VerifyMobileMoneyOTPSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        response = verify_mobile_money_otp(serializer.validated_data)

        return Response(response)


class MobileMoneyNetworksView(APIView):

    def get(self, request):

        response = fetch_mobile_money_networks()

        return Response(response)


class BankListView(APIView):

    def get(self, request):

        currency = request.query_params.get("currency")

        response = fetch_banks(currency=currency)

        return Response(response)
