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
            return query.first().first_name + "-" + f'{self.amount:,} T'
        return self.mail + "-" + f'{self.amount:,} T'


class ManualPaymentReport(models.Model):
    amount = models.IntegerField(null=False, blank=False)  # Rial
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + "-" + self.get_amount_pretty()

    def get_amount_pretty(self):
        return f'{self.amount:,} T'

    get_amount_pretty.short_description = "Amount"


@receiver(post_save, sender=ManualPaymentReport)
def create_backup_thread(sender, instance: ManualPaymentReport, **kwargs):
    current_credit = Credit.get_credit(instance.user)
    new_credit = instance.amount + current_credit
    Credit(reminded_credit=new_credit, user=instance.user, manual_payment=instance).save()


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

    def get_human_readable_pay_amount(self):
        return f'{self.amount:,} T'

    get_human_readable_pay_amount.short_description = "Amount"

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
    manual_payment = models.ForeignKey(to=ManualPaymentReport, default=None, on_delete=models.SET_NULL, null=True,
                                       blank=True)
    is_last_credit = models.BooleanField(default=True)

    def get_reminded_credit_pretty(self):
        return f'{self.reminded_credit:,} T'

    get_reminded_credit_pretty.short_description = "Amount"

    def __str__(self):
        tag = str(self.id)
        if Credit.objects.filter(user=self.user).last() == self:
            tag = 'last'
        return self.user.first_name + "-" + self.get_reminded_credit_pretty()

    @staticmethod
    def get_credit(user):
        query = Credit.objects.filter(user=user)
        if not query.exists():
            return 0
        return query.last().reminded_credit


@receiver(post_save, sender=Credit)
def credit_created_handler(sender, instance, created, **kwargs):
    if created:
        last_credit = Credit.objects.filter(user=instance.user).exclude(id=instance.id).order_by('-id').first()
        if last_credit is not None:
            last_credit.is_last_credit = False
            last_credit.save()
