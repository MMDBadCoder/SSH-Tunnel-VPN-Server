import json
from datetime import datetime

import pytz as pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from VpnServer.settings import VALID_RANGE_OF_DAYS, EACH_DAY_PRICE
from packs.models import Pack
from payment.models import WebhookReports, PaymentKey, Credit, PaymentFactor


@csrf_exempt
def webhook(request, pay_key):
    if PaymentKey.get_key() != pay_key:
        return HttpResponseBadRequest("Wrong pay key!")

    try:
        data = json.loads(request.body)
        amount = int(data['amount'])
        payer = data['payer']
        name = payer['name']
        mail = payer['mail']
        mail = mail.strip().lower()
        desc = payer['desc']
        phone = payer['phone']
        timestamp = data['payment']['date']
        dt = datetime.fromtimestamp(int(timestamp), tz=pytz.timezone('Asia/Tehran'))
        print("Data of webhook request was extracted")
        webhook_report = WebhookReports(phone_number=phone, name=name, amount=amount, mail=mail, dt=dt, desc=desc)
        webhook_report.save()
        print("Webhook report was generated")
        user = User.objects.filter(username=mail)
        if user.exists():
            print("Related user of this webhook was detected")
            user = user.first()
            toman_amount = (amount / 10)
            current_credit = Credit.get_credit(user)
            new_credit = toman_amount + current_credit
            Credit(reminded_credit=new_credit, user=user, payment_factor=None, webhook_report=webhook_report).save()
            print("Credit was updated")
        else:
            print("------ User by this mail not found ------")
            print(mail)
        return HttpResponse(status=200)
    except Exception as e:
        print("Error at webhook:")
        print(e)
        return HttpResponseBadRequest("Only post available")


@login_required
@csrf_exempt
def buy_new_pack(request, pack_days):
    if PaymentFactor.objects.filter(user=request.user, payed=False).exists():
        return HttpResponseBadRequest("You have some not payed factors!")

    if pack_days not in VALID_RANGE_OF_DAYS:
        return HttpResponseBadRequest("Requested days is not valid")

    pack = Pack(user=request.user, days=pack_days)
    needed_credit = EACH_DAY_PRICE * pack_days
    factor = PaymentFactor(user=request.user, pay_for=PaymentFactor.PayFor.BUY_PACK, related_pack=pack,
                           amount=needed_credit, payed=False)
    if not factor.can_pay():
        return HttpResponseBadRequest("Not enough credit to buy this pack")

    pack.save()
    factor.save()
    factor.pay()

    return HttpResponse(status=200)


@login_required
def pay_factor(request, factor_id):
    factor = PaymentFactor.objects.get(id=factor_id)
    if factor.user != request.user:
        return HttpResponseBadRequest("No permission")
    if factor.payed:
        return HttpResponseBadRequest("This factor has been payed in past")
    if not factor.can_pay():
        return HttpResponseBadRequest("Not enough credit to pay this factor")
    factor.pay()
    return redirect('user-home')
