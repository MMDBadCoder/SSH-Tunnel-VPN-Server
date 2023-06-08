from django.db import models
from django.utils.translation import gettext_lazy as _


class GiftPack(models.Model):
    days = models.IntegerField(default=0, blank=False, null=False)
    free_traffic = models.BooleanField(default=False, blank=False, null=False)
    all_users = models.BooleanField(default=False, blank=False, null=False)
    active_users = models.BooleanField(default=True, blank=False, null=False)
    label = models.CharField(max_length=100, default=None, null=True, blank=True)

    def __str__(self):
        return 'gift' + str(self.id) + '-' + self.label


class HomeMessage(models.Model):
    class Type(models.TextChoices):
        positive = 'positive', _('Positive')
        info = 'info', _('Info')
        negative = 'negative', _('Negative')
        warn = 'warning', _('Warning')
        error = 'error', _('Error')

    title = models.CharField(max_length=100, default='', blank=True, null=False)
    message = models.CharField(max_length=1000, null=False, blank=False)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.positive, null=False, blank=False)

    def __str__(self):
        return self.title + "-msg-" + str(self.id)
