import subprocess
import time
from datetime import timedelta

from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render

from VpnServer.settings import STARTUP_TIME, REBOOT_PERIOD_SECONDS, HOSTNAME
from packs.models import Pack


# Create your views here.
@login_required
@user_passes_test(lambda u: u.is_superuser)
def monitoring_page(request):
    running_time = time.time() - STARTUP_TIME
    reminded_seconds_to_reboot = int(REBOOT_PERIOD_SECONDS - running_time)

    data = {
        'packs': Pack.objects.filter(started=True, finished=False).order_by('-id'),
        'HOSTNAME': HOSTNAME,
        "TIME_TO_REBOOT": timedelta(seconds=reminded_seconds_to_reboot),
        'CONNECTED': all_connection_count()
    }

    return render(request, 'monitor.html', data)


def all_connection_count():
    command = "ps ax | grep ssh | grep '\[priv\]'"
    result = subprocess.run([command], stdout=subprocess.PIPE, shell=True)
    result = result.stdout.decode('utf-8').strip()
    if result == '':
        return 0
    return len(result.split('\n'))
