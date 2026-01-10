import hmac
import hashlib
import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .models import Payment

@csrf_exempt
def paystack_webhook(request):
    payload = request.body
    signature = request.headers.get('x-paystack-signature')

    computed_signature = hmac.new(
        key=settings.PAYSTACK_SECRET_KEY.encode(),
        msg=payload,
        digestmod=hashlib.sha512
    ).hexdigest()

    if signature != computed_signature:
        return HttpResponse(status=400)

    event = json.loads(payload)

    if event['event'] == 'charge.success':
        reference = event['data']['reference']
        metadata = event['data']['metadata']
        order_id = metadata.get('order_id')

        try:
            payment = Payment.objects.get(reference=reference)
            payment.status = 'succeeded'
            payment.save()

            order = Order.objects.get(id=order_id)
            order.status = 'paid'
            order.save()
        except (Payment.DoesNotExist, Order.DoesNotExist):
            pass

    return HttpResponse(status=200)
