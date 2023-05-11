from django import forms

from backup_system.models import BackupFile


class BackupForm(forms.ModelForm):
    class Meta:
        model = BackupFile
        fields = ('file',)
