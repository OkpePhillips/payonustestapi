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
    VirtualAccountResponseSerializer,
    FixedVirtualAccountSerializer,
)

from .services.payments import (
    create_dynamic_virtual_account,
    create_fixed_virtual_account,
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
