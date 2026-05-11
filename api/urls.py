from django.urls import path

from .views import (
    CreateDynamicVirtualAccountView,
)


urlpatterns = [
    path(
        "payments/dynamic-account/",
        CreateDynamicVirtualAccountView.as_view(),
        name="dynamic-account",
    ),
]
