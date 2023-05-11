import os
import shutil

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect

from VpnServer.settings import BASE_DIR, MEDIA_ROOT
from backup_system.forms import BackupForm

SQLITE_PATH = os.path.join(BASE_DIR, 'db.sqlite3')


@login_required
def download_backup(request):
    if os.path.exists(SQLITE_PATH):
        with open(SQLITE_PATH, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(SQLITE_PATH)
            return response
    raise Http404


@login_required
def backup_inject(request):
    form = BackupForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponseBadRequest()

    uploaded_db = form.files['db']
    with open(SQLITE_PATH, 'wb+') as destination:
        for chunk in uploaded_db.chunks():
            destination.write(chunk)

    return redirect('backup-page')


@login_required
def backup_page(request):
    return render(request, 'backup.html')
