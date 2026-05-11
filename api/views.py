from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

from .serializers import (
    DynamicVirtualAccountSerializer,
    VirtualAccountResponseSerializer,
)

from .services.payments import create_dynamic_virtual_account


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

        virtual_account = create_dynamic_virtual_account(serializer.validated_data)

        response_serializer = VirtualAccountResponseSerializer(virtual_account)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
