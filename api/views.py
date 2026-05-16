from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json

from rest_framework.parsers import JSONParser
from .parsers import PlainTextParser

from api.services.payouts import (
    initiate_bank_transfer,
    initiate_bulk_bank_transfer,
    initiate_eft_payout,
    initiate_mobile_money_payout,
    perform_name_enquiry,
)
from api.services.wallets import (
    fetch_wallet_transactions,
    fetch_wallets,
    wallet_to_wallet_transfer,
)
from api.services.webhooks import process_payonus_webhook, verify_webhook_signature
from .models import WebhookLog
from .serializers import (
    BankTransferSerializer,
    BulkTransferSerializer,
    DynamicVirtualAccountSerializer,
    EFTPayoutSerializer,
    FundSandboxWalletSerializer,
    MobileMoneyCollectionSerializer,
    MobileMoneyPayoutSerializer,
    NameEnquirySerializer,
    VerifyMobileMoneyOTPSerializer,
    VerifySinglePaymentSerializer,
    VirtualAccountResponseSerializer,
    FixedVirtualAccountSerializer,
    WalletTransferSerializer,
    WebhookLogSerializer,
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
    list_payin_payment_requests,
    verify_mobile_money_otp,
    verify_single_payment,
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

        if (
            isinstance(virtual_account, dict)
            and virtual_account.get("success") is False
        ):
            return Response(virtual_account, status=400)

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
    parser_classes = [JSONParser, PlainTextParser]

    def post(self, request):

        payload = request.data

        if isinstance(payload, str):
            payload = json.loads(payload)

        received_hash = request.headers.get("hash", "")

        is_valid = verify_webhook_signature(
            payload=payload,
            received_hash=received_hash,
        )

        if not is_valid:
            return Response(
                {
                    "success": False,
                    "message": "Invalid webhook signature",
                },
                status=400,
            )

        result = process_payonus_webhook(
            payload=payload,
            signature=received_hash,
        )

        return Response(
            {
                "success": True,
                "message": "Webhook received",
                "result": result,
            },
            status=200,
        )


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
                "status",
                openapi.IN_QUERY,
                description="Transfer status",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "currency",
                openapi.IN_QUERY,
                description="Currency code",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "transferType",
                openapi.IN_QUERY,
                description="Transfer type",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "merchantReference",
                openapi.IN_QUERY,
                description="Merchant reference",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "onusReference",
                openapi.IN_QUERY,
                description="Payonus reference",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "createdFrom",
                openapi.IN_QUERY,
                description="Start date YYYY-MM-DD",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "createdTo",
                openapi.IN_QUERY,
                description="End date YYYY-MM-DD",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "Transfer requests retrieved"},
        operation_summary="List Transfer Requests",
        operation_description=(
            "Retrieve payout transfer requests " "with optional filtering."
        ),
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
        operation_summary=("Wallet to Wallet Transfers - Payout"),
        operation_description=("Wallet to Wallet Transfers - Payout"),
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
                description="filter parameter",
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


class PayonusWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        signature = (
            request.headers.get("X-Webhook-Signature")
            or request.headers.get("X-Payonus-Signature")
            or request.headers.get("signature")
            or ""
        )

        result = process_payonus_webhook(
            payload=request.data,
            signature=signature,
        )

        return Response(
            {
                "success": True,
                "message": "Webhook received",
                "result": result,
            },
            status=200,
        )


class PayonusWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        received_hash = request.headers.get("hash", "")

        is_valid = verify_webhook_signature(
            payload=request.data,
            received_hash=received_hash,
        )

        if not is_valid:
            return Response(
                {
                    "success": False,
                    "message": "Invalid webhook signature",
                },
                status=400,
            )

        result = process_payonus_webhook(
            payload=request.data,
            signature=received_hash,
        )

        return Response(
            {
                "success": True,
                "message": "Webhook received",
                "result": result,
            },
            status=200,
        )


class VerifySinglePaymentView(APIView):

    @swagger_auto_schema(
        request_body=(VerifySinglePaymentSerializer),
        responses={201: (VerifySinglePaymentSerializer)},
        operation_summary=("Verify Single Payment using onus reference"),
        operation_description=(
            "Retrieves the latest status of a payin using the Payonus "
            "onusReference. Applies to dynamic accounts, fixed accounts, "
            "wallet links, and mobile money collections."
        ),
    )
    def post(self, request):
        serializer = VerifySinglePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = verify_single_payment(serializer.validated_data)

        return Response(response)


class BulkTransferView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="CSV file containing bulk transfer rows",
            ),
            openapi.Parameter(
                name="description",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                description="Description of the bulk transfer batch",
            ),
            openapi.Parameter(
                name="transfer_type",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                default="WALLET_TO_BANK_ACCOUNT",
                description="Transfer type",
            ),
            openapi.Parameter(
                name="country_code",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                default="NG",
                description="Country code",
            ),
            openapi.Parameter(
                name="currency",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                default="NGN",
                description="Currency code",
            ),
            openapi.Parameter(
                name="notification_url",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                description="Optional webhook URL",
            ),
            openapi.Parameter(
                name="momo_network",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                description="Mobile money network, if applicable",
            ),
        ],
        operation_summary="Initiate Bulk Bank Transfer",
        operation_description=(
            "Uploads a CSV file and initiates multiple transfers "
            "through the Payonus bulk bank transfer endpoint."
        ),
        responses={200: "Bulk transfer response"},
    )
    def post(self, request):
        serializer = BulkTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = initiate_bulk_bank_transfer(serializer.validated_data)

        return Response(response)


class PayinPaymentRequestListView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("status", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("businessId", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("reference", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter(
                "onusReference", openapi.IN_QUERY, type=openapi.TYPE_STRING
            ),
            openapi.Parameter("fromDate", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("toDate", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("size", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ],
        operation_summary="List Payment Requests",
        operation_description="List payin/payment requests with optional filters.",
        responses={200: "Payment requests retrieved"},
    )
    def get(self, request):
        allowed_filters = [
            "status",
            "businessId",
            "reference",
            "onusReference",
            "fromDate",
            "toDate",
            "page",
            "size",
        ]

        params = {}

        for field in allowed_filters:
            value = request.query_params.get(field)

            if value is not None:
                params[field] = value

        if "businessId" not in params:
            params["businessId"] = settings.PAYONUS_BUSINESS_ID

        response = list_payin_payment_requests(params=params)

        return Response(response)


class WebhookLogListView(APIView):
    def get(self, request):
        logs = WebhookLog.objects.all().order_by("-created_at")[:100]
        serializer = WebhookLogSerializer(logs, many=True)
        return Response(serializer.data)
