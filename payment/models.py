import random
import string

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from packs.models import Pack


class WebhookReports(models.Model):
    amount = models.IntegerField(null=False, blank=False)  # Rial
    name = models.TextField(max_length=100, null=False, blank=False)
    dt = models.DateTimeField(null=False, blank=False)
    mail = models.TextField(max_length=100, null=False, blank=False)
    desc = models.TextField(max_length=100, null=True, blank=True, default='No desc')
    phone_number = models.TextField(max_length=20, null=False, blank=False)

    def __str__(self):
        query = User.objects.filter(email=self.mail)
        if query.exists():
            return query.first().first_name + "-" + str(self.amount)
        return self.mail + "-" + str(self.amount)


class ManualPaymentReport(models.Model):
    amount = models.IntegerField(null=False, blank=False)  # Rial
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)


@receiver(post_save, sender=ManualPaymentReport)
def create_backup_thread(sender, instance: ManualPaymentReport, **kwargs):
    current_credit = Credit.get_credit(instance.user)
    new_credit = instance.amount + current_credit
    Credit(reminded_credit=new_credit, user=instance.user, payment_factor=None, webhook_report=None).save()


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


class PaymentFactor(models.Model):
    class PayFor(models.TextChoices):
        BUY_PACK = 'BP', _('Buy pack')
        TRAFFIC_USAGE = 'TU', _('Traffic usage')
        PACK_EXTENSION = 'PE', _('Pack extension')

    pay_for = models.CharField(max_length=20, null=True, blank=True, choices=PayFor.choices)
    amount = models.IntegerField(blank=False, null=False, default=0)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=False)
    related_pack = models.ForeignKey(to=Pack, null=True, default=None, on_delete=models.SET_NULL)
    payed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + "-" + str(self.amount) + "-" + self.pay_for

    def can_pay(self):
        if Credit.get_credit(self.user) >= self.amount:
            return True

    def pay(self):
        current_credit = Credit.get_credit(self.user)
        after_pay_credit = current_credit - self.amount
        Credit(reminded_credit=after_pay_credit, user=self.user, payment_factor=self).save()
        self.payed = True
        self.save()


class Credit(models.Model):
    reminded_credit = models.IntegerField(default=0, blank=False, null=False)  # Toman
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    payment_factor = models.ForeignKey(to=PaymentFactor, on_delete=models.SET_NULL, null=True, blank=True)
    webhook_report = models.ForeignKey(to=WebhookReports, default=None, on_delete=models.SET_NULL, null=True,
                                       blank=True)

    def __str__(self):
        tag = str(self.id)
        if Credit.objects.filter(user=self.user).last() == self:
            tag = 'latest'
        return self.user.first_name + "-" + str(self.reminded_credit) + "-" + tag

    @staticmethod
    def get_credit(user):
        query = Credit.objects.filter(user=user)
        if not query.exists():
            return 0
        return query.last().reminded_credit
