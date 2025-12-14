from django.views import View
from django.http import JsonResponse

class StripePaymentView(View):
	def get(self, request):
		return JsonResponse({"provider": "stripe", "status": "ok"})

class PayPalPaymentView(View):
	def get(self, request):
		return JsonResponse({"provider": "paypal", "status": "ok"})

class MadaPaymentView(View):
	def get(self, request):
		return JsonResponse({"provider": "mada", "status": "ok"})

