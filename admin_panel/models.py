import subprocess

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _


class GiftPack(models.Model):
    days = models.IntegerField(default=0, blank=False, null=False)
    free_traffic = models.BooleanField(default=False, blank=False, null=False)
    all_users = models.BooleanField(default=False, blank=False, null=False)
    active_users = models.BooleanField(default=True, blank=False, null=False)
    title = models.CharField(max_length=100, default=None, null=True, blank=True)

    def __str__(self):
        return 'gift' + str(self.id) + '-' + self.title


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


class MigrateServer(models.Model):
    server_host = models.CharField(max_length=100, blank=False, null=False)
    server_ssh_port = models.IntegerField(default=22)
    server_ssh_username = models.CharField(max_length=100, default='root', blank=False, null=False)
    server_ssh_password = models.CharField(max_length=100, blank=False, null=False)

    def get_logs_url(self):
        return mark_safe(f'<a href="/static/migrate{str(self.id)}.log">Download</a>')

    get_logs_url.short_description = "Log File"


@receiver(post_save, sender=MigrateServer)
def migrate_created_handler(sender, instance: MigrateServer, created, **kwargs):
    if created:
        log_file = f"./static/migrate{instance.id}.log"
        script = "./migrate_and_setup.sh"
        args = [script, instance.server_host, str(instance.server_ssh_port), instance.server_ssh_username,
                instance.server_ssh_password]

        with open(log_file, 'w') as f:
            subprocess.Popen(args, stdout=f, stderr=subprocess.STDOUT)
        print(script + ' ' + ' '.join(args))
        print(f"Migration started. Log will be saved to {log_file}")
