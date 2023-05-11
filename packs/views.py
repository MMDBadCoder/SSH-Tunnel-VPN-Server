import time
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render, redirect

from VpnServer import settings
from VpnServer.settings import HOSTNAME, REBOOT_PERIOD_SECONDS, STARTUP_TIME
from packs.models import Pack


@login_required
def home_view(request):
    data = {
        'EACH_WEEK_PRICE': settings.EACH_WEEK_PRICE,
        'IDPAY_PAYMENT_PAGE_URL': settings.IDPAY_PAYMENT_PAGE_URL,
        'packs': Pack.objects.filter(user=request.user).order_by('-id'),
        'HOSTNAME': settings.HOSTNAME
    }
    return render(request, 'home.html', data)


@login_required
def start_pack(request, pack_id):
    Pack.objects.get(id=pack_id).run_pack()
    return redirect('user-home')


@login_required
def get_putty_shell_file(request, pack_id):
    pack = Pack.objects.get(id=pack_id)
    content = f'START /B putty.exe -D 10808 -ssh {pack.linux_username}@{HOSTNAME} {pack.port} -pw {pack.linux_password}'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format('proxy.cmd')
    return response


@login_required
def get_linux_shell(request, pack_id):
    pack = Pack.objects.get(id=pack_id)
    content = f"sshpass -p \"{pack.linux_password}\" ssh -oStrictHostKeyChecking=no -D 10808 -C -q -N {pack.linux_username}@{HOSTNAME} -p {pack.port}"
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format('proxy.sh')
    return response


@login_required
def monitor_packs(request):
    if not request.user.is_staff:
        return HttpResponseNotFound("Not found")

    running_time = time.time() - STARTUP_TIME
    reminded_seconds_to_reboot = int(REBOOT_PERIOD_SECONDS - running_time)

    data = {
        'packs': Pack.objects.filter(started=True, finished=False).order_by('-id'),
        'HOSTNAME': settings.HOSTNAME,
        "TIME_TO_REBOOT": timedelta(seconds=reminded_seconds_to_reboot)
    }

    return render(request, 'monitor.html', data)
