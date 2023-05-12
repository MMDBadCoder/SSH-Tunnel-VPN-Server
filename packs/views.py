import paramiko
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from paramiko import SSHClient

from VpnServer import settings
from VpnServer.settings import HOSTNAME
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
def test_pack_connection(request, pack_id):
    pack = Pack.objects.get(id=pack_id)

    successful = False
    with SSHClient() as client:
        try:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(HOSTNAME, port=pack.port, username=pack.linux_username,
                           password=pack.linux_password, timeout=3)
            successful = True
        except Exception as e:
            print(e)

    return HttpResponse(status=200, content=successful)
