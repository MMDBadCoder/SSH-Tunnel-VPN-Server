import os
import time
from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect

from VpnServer.settings import HOSTNAME, STARTUP_TIME, REBOOT_PERIOD_SECONDS
from VpnServer.wsgi import reboot_os
from packs.models import Pack
from payment.models import PaymentKey


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_panel_page(request):
    running_time = time.time() - STARTUP_TIME
    reminded_seconds_to_reboot = int(REBOOT_PERIOD_SECONDS - running_time)
    data = {
        'TIME_TO_REBOOT': timedelta(seconds=reminded_seconds_to_reboot),
        'CONNECTIONS_COUNT': Pack.all_connection_count(),
        'ACTIVE_PACKS_COUNT': Pack.objects.filter(started=True, finished=False).count(),
        'PAYMENT_WEB_HOOK': PaymentKey.get_key(),
        'HOSTNAME': HOSTNAME
    }

    return render(request, 'admin-panel.html', data)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def active_packs(request):
    data = {
        'CONNECTIONS_COUNT': Pack.all_connection_count(),
        'packs': Pack.objects.filter(started=True, finished=False).order_by('-id'),
        'HOSTNAME': HOSTNAME
    }

    return render(request, 'active-packs.html', data)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def reboot(request):
    reboot_os()


@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_restart(request):
    os.system("systemctl restart mmdvpn")
    return redirect('admin-panel')


def migrate(request):
    if request.POST:
        ip = request.POST['server-ip']
        port = request.POST['port']
        username = request.POST['username']
        password = request.POST['password']

    return render(request, 'migrate.html')
