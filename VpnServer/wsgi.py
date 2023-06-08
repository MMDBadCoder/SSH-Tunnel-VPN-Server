import os
import threading
from time import sleep

from django.core.wsgi import get_wsgi_application

from VpnServer.settings import REBOOT_PERIOD_SECONDS
from packs.models import check_finished_packs, init_sshd_services, Pack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VpnServer.settings')

application = get_wsgi_application()

threading.Thread(target=check_finished_packs, daemon=True).start()

init_sshd_services()


def reboot_os():
    for pack in Pack.objects.filter(started=True, finished=False):
        pack.flush_usage_of_after_startup()
    os.system('reboot')


def reboot_thread():
    sleep(REBOOT_PERIOD_SECONDS)
    reboot_os()


threading.Thread(target=reboot_thread, daemon=True).start()
