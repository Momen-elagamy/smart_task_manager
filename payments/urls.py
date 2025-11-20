from django.urls import path
from .views import StripePaymentView, PayPalPaymentView, MadaPaymentView

urlpatterns = [
    path('stripe/', StripePaymentView.as_view(), name='stripe-payment'),
    path('paypal/', PayPalPaymentView.as_view(), name='paypal-payment'),
    path('mada/', MadaPaymentView.as_view(), name='mada-payment'),
]
