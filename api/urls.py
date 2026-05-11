from django.urls import path

from .views import (
    CreateDynamicVirtualAccountView,
    CreateFixedVirtualAccountView,
    PayonusWebhookView,
)

urlpatterns = [
    path(
        "payments/dynamic-account/",
        CreateDynamicVirtualAccountView.as_view(),
        name="dynamic-account",
    ),
    path(
        "payments/fixed-account/",
        CreateFixedVirtualAccountView.as_view(),
        name="fixed-account",
    ),
    path(
        "webhooks/payonus/",
        PayonusWebhookView.as_view(),
        name="payonus-webhook",
    ),
]
