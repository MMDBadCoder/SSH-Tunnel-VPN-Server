from django.db import models


class BackupFile(models.Model):
    file = models.FileField(upload_to='db/', blank=True)
