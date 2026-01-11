import uuid
import json
import hmac
import hashlib
import requests

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages

from orders.models import Order
from .models import Payment


def choose_payment_method(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        method = request.POST.get('payment_method')
        phone = request.POST.get('phone_number')

        reference = str(uuid.uuid4())

        Payment.objects.create(
            order=order,
            payment_method=method,
            amount=order.total_price,
            phone_number=phone if method == 'momo' else None,
            reference=reference,
            status='processing'
        )

        return redirect('payments:paystack_payment', order.id)

    return render(request, 'payments/choose_method.html', {'order': order})

# Display Paystack payment page
def paystack_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "payments/paystack_page.html", {"order": order})


def generate_reference():
    return f"PAY-{uuid.uuid4().hex[:12].upper()}"



# Initiate Paystack payment
def paystack_payment(request, order_id):
    if request.method != "POST":
        return redirect("orders:order_success", order_id=order_id)

    order = get_object_or_404(Order, id=order_id)

    payment = Payment.objects.filter(
        order=order,
        payment_method="paystack",
        status__in=["processing", "pending"]
    ).first()

    if not payment:
        payment = Payment.objects.create(
            order=order,
            amount=order.total_price,
            payment_method="paystack",
            status="processing",
            reference=generate_reference(),  # ✅ IMPORTANT
        )

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": order.email,
        "amount": int(payment.amount * 100),
        "reference": payment.reference,  # ✅ Paystack reference
        "callback_url": request.build_absolute_uri(
            reverse("payments:paystack_verify")
        ),
        "metadata": {
            "order_id": order.id,
            "payment_id": payment.id,
        },
    }

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=data,
        headers=headers,
        timeout=30,
    )

    result = response.json()

    if result.get("status") is True:
        return redirect(result["data"]["authorization_url"])

    payment.status = "failed"
    payment.save()

    messages.error(request, "Payment initialization failed.")
    return redirect("orders:order_success", order_id=order.id)

# Verify Paystack payment

def paystack_verify(request):
    reference = request.GET.get("reference")
    payment = get_object_or_404(Payment, reference=reference)
    if not reference:
        return redirect("products:product_list")

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers=headers,
    )

    result = response.json()

    if result.get("status") and result["data"]["status"] == "success":
        metadata = result["data"]["metadata"]
        payment = Payment.objects.get(id=metadata["payment_id"])
        payment.status = "completed"
        payment.save()

        order = payment.order
        order.status = "paid"
        order.save()

        return redirect("orders:order_success", order_id=order.id)

    return redirect("orders:order_success", order_id=metadata["order_id"])



def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})


def payment_failed(request):
    return render(request, 'payments/payment_failed.html')


@csrf_exempt
def paystack_webhook(request):
    payload = request.body
    signature = request.headers.get('x-paystack-signature')

    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    if signature != computed_signature:
        return HttpResponse(status=400)

    event = json.loads(payload)

    if event['event'] == 'charge.success':
        data = event['data']
        reference = data['reference']
        order_id = data['metadata'].get('order_id')

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
