import random
import string

from django.contrib.auth.models import User
from django.db import models

from packs.models import Pack


class WebhookReports(models.Model):
    amount = models.IntegerField(null=False, blank=False)
    name = models.TextField(max_length=100, null=False, blank=False)
    dt = models.DateTimeField(null=False, blank=False)
    mail = models.TextField(max_length=100, null=False, blank=False)
    desc = models.TextField(max_length=100, null=True, blank=True, default='No desc')
    phone_number = models.TextField(max_length=20, null=False, blank=False)


class PaymentKey(models.Model):
    key = models.CharField(max_length=100, default=None, null=True, blank=False)

    @staticmethod
    def get_key():
        if PaymentKey.objects.count() > 1:
            PaymentKey.objects.all().delete()

        if PaymentKey.objects.count() == 0:
            letters = string.ascii_lowercase + string.digits
            key = ''.join(random.choice(letters) for _ in range(20))
            PaymentKey(key=key).save()
            return key

        return PaymentKey.objects.first().key
