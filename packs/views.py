from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render, redirect

from VpnServer import settings
from packs.models import Pack


@login_required
def home_view(request):
    data = {
        'EACH_WEEK_PRICE': settings.EACH_WEEK_PRICE,
        'IDPAY_PAYMENT_PAGE_URL': settings.IDPAY_PAYMENT_PAGE_URL,
        'packs': Pack.objects.filter(user=request.user),
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
    content = f'START /B putty.exe -D 10808 -ssh {pack.linux_username}@hajmmd.ir {pack.port} -pw {pack.linux_password}'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format('proxy.cmd')
    return response


@login_required
def all_active_packs(request):
    if not request.user.is_staff:
        return HttpResponseNotFound("Not found")
    data = {
        'packs': Pack.objects.filter(started=True, finished=False),
        'HOSTNAME': settings.HOSTNAME
    }
    return render(request, 'active-packs.html', data)
