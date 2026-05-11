from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.services.payouts import (
    initiate_bank_transfer,
    initiate_eft_payout,
    initiate_mobile_money_payout,
    perform_name_enquiry,
)
from api.services.wallets import fetch_wallet_transactions, fetch_wallets, wallet_to_wallet_transfer
from .models import WebhookLog
from .serializers import (
    BankTransferSerializer,
    DynamicVirtualAccountSerializer,
    EFTPayoutSerializer,
    FundSandboxWalletSerializer,
    MobileMoneyCollectionSerializer,
    MobileMoneyPayoutSerializer,
    NameEnquirySerializer,
    VerifyMobileMoneyOTPSerializer,
    VirtualAccountResponseSerializer,
    FixedVirtualAccountSerializer,
    WalletTransferSerializer,
)

from .services.payments import (
    create_dynamic_virtual_account,
    create_fixed_virtual_account,
    fetch_banks,
    fetch_mobile_money_networks,
    fetch_transfer_requests,
    fund_sandbox_ngn_wallet,
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


class NameEnquiryView(APIView):

    @swagger_auto_schema(
        request_body=(NameEnquirySerializer),
        responses={201: (NameEnquirySerializer)},
        operation_summary=("Name enquiry"),
        operation_description=("Confirm bank name before making transfer"),
    )
    def post(self, request):

        serializer = NameEnquirySerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        response = perform_name_enquiry(serializer.validated_data)

        return Response(response)


class BankTransferView(APIView):

    @swagger_auto_schema(
        request_body=(BankTransferSerializer),
        responses={201: (BankTransferSerializer)},
        operation_summary=("Bank Transfer"),
        operation_description=("Initiating bank transfer"),
    )
    def post(self, request):

        serializer = BankTransferSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        response = initiate_bank_transfer(serializer.validated_data)

        return Response(response)


class FundSandboxWalletView(APIView):

    @swagger_auto_schema(
        request_body=(FundSandboxWalletSerializer),
        responses={201: (FundSandboxWalletSerializer)},
        operation_summary=("Fund Sandbox"),
        operation_description=("Funding the sandbox to be able to test transfer"),
    )
    def post(self, request):

        serializer = FundSandboxWalletSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        response = fund_sandbox_ngn_wallet(serializer.validated_data)

        return Response(response)


class TransferRequestListView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "parameter_name",
                openapi.IN_QUERY,
                description="A description of what this optional param does",
                type=openapi.TYPE_STRING,
                required=False,  # This makes it optional
            ),
        ],
        responses={201: (FundSandboxWalletSerializer)},
        operation_summary=("Fund Sandbox"),
        operation_description=("Funding the sandbox to be able to test transfer"),
    )
    def get(self, request):

        params = {}

        query_fields = [
            "merchantId",
            "id",
            "status",
            "onusReference",
            "accountNumber",
            "merchantReference",
            "businessIds",
            "channel",
            "transferType",
            "currency",
            "reversed",
            "refund",
            "createdFrom",
            "createdTo",
        ]

        for field in query_fields:

            value = request.query_params.get(field)

            if value is not None:
                params[field] = value

        response = fetch_transfer_requests(params=params)

        return Response(response)


class MobileMoneyPayoutView(APIView):

    @swagger_auto_schema(
        request_body=(MobileMoneyPayoutSerializer),
        responses={201: (MobileMoneyPayoutSerializer)},
        operation_summary=("Payout with momo"),
        operation_description=("Mobile money payout transfer"),
    )
    def post(self, request):
        serializer = MobileMoneyPayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = initiate_mobile_money_payout(serializer.validated_data)

        return Response(response)


class EFTPayoutView(APIView):

    @swagger_auto_schema(
        request_body=(EFTPayoutSerializer),
        responses={201: (EFTPayoutSerializer)},
        operation_summary=("EFT payout"),
        operation_description=("Payout with eft"),
    )
    def post(self, request):
        serializer = EFTPayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = initiate_eft_payout(serializer.validated_data)

        return Response(response)


class WalletListView(APIView):
    def get(self, request):
        response = fetch_wallets()
        return Response(response)


class WalletTransferView(APIView):

    @swagger_auto_schema(
        request_body=(WalletTransferSerializer),
        responses={201: (WalletTransferSerializer)},
        operation_summary=("EFT payout"),
        operation_description=("Payout with eft"),
    )
    def post(self, request):
        serializer = WalletTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = wallet_to_wallet_transfer(serializer.validated_data)
        return Response(response)


class WalletTransactionListView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "parameter_name",
                openapi.IN_QUERY,
                description="A description of what this optional param does",
                type=openapi.TYPE_STRING,
                required=False,  # This makes it optional
            ),
        ],
        responses={201: (FundSandboxWalletSerializer)},
        operation_summary=("Fund Sandbox"),
        operation_description=("Funding the sandbox to be able to test transfer"),
    )
    def get(self, request):
        allowed_params = [
            "pageNo",
            "pageSize",
            "createdFrom",
            "createdTo",
            "transactionType",
            "currency",
            "onusReference",
            "product",
        ]

        params = {}

        for field in allowed_params:
            value = request.query_params.get(field)
            if value:
                params[field] = value

        response = fetch_wallet_transactions(params)
        return Response(response)
