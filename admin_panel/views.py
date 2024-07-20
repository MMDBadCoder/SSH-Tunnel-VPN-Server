import os
import shutil
import time

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from VpnServer.settings import HOSTNAME, STARTUP_TIME
from packs.models import Pack
from payment.models import PaymentKey


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_panel_page(request):
    running_time = time.time() - STARTUP_TIME
    data = {
        'CONNECTIONS_COUNT': Pack.all_connection_count(),
        'ACTIVE_PACKS_COUNT': Pack.get_active_packs().count(),
        'PAYMENT_WEB_HOOK': PaymentKey.get_key(),
        'HOSTNAME': HOSTNAME
    }

    return render(request, 'admin-panel.html', data)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def active_packs(request):
    data = {
        'CONNECTIONS_COUNT': Pack.all_connection_count(),
        'packs': Pack.get_active_packs().order_by('-id'),
        'HOSTNAME': HOSTNAME
    }

    return render(request, 'active-packs.html', data)


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

        archive_folder_name = 'archive'
        if os.path.exists(archive_folder_name):
            shutil.rmtree(archive_folder_name)
        os.mkdir(archive_folder_name)
        for file_dir_name in os.listdir('.'):
            if file_dir_name not in ['venv'] and not file_dir_name.startswith('.'):
                if os.path.isdir(file_dir_name):
                    shutil.copytree(file_dir_name, archive_folder_name + '/' + file_dir_name)
                else:
                    shutil.copy(file_dir_name, archive_folder_name)



    return render(request, 'migrate.html')
