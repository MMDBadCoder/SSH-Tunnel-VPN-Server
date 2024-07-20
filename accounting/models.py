from django.contrib.auth.models import User

from payment.models import ManualPaymentReport, WebhookReports


def get_first_name(user):
    return user.first_name


User.add_to_class("__str__", get_first_name)
