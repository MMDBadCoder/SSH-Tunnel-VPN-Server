import json
from datetime import datetime

import pytz as pytz
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from VpnServer.settings import EACH_WEEK_PRICE
from packs.models import Pack
from payment.models import WebhookReports, PaymentKey


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
        WebhookReports.objects.create(phone_number=phone, name=name, amount=amount, mail=mail, dt=dt, desc=desc)
        print("Webhook report was generated")
        user = User.objects.filter(username=mail)
        if user.exists():
            print("Related user of this webhook was detected")
            user = user.first()
            days = 7 * ((amount / 10) / EACH_WEEK_PRICE)
            Pack.objects.create(user=user, days=days)
            print("Pack was generated")
        else:
            print("------ User by this mail not found ------")
            print(mail)
        return HttpResponse(status=200)
    except Exception as e:
        print("Error at webhook:")
        print(e)
        return HttpResponseBadRequest("Only post available")
