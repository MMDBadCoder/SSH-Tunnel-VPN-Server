import os
import threading
from time import sleep

from django.core.wsgi import get_wsgi_application

from VpnServer.settings import REBOOT_PERIOD_SECONDS, RUNNING_SERVER
from packs.models import check_finished_packs, init_active_packs_sessions, Pack, TempUsageTraffic

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VpnServer.settings')

application = get_wsgi_application()


def reboot_os():
    for pack in Pack.get_active_packs():
        pack.flush_usage_of_after_startup()
    os.system('reboot')


def reboot_thread():
    sleep(REBOOT_PERIOD_SECONDS)
    reboot_os()


def update_temp_usage_thread():
    while True:
        sleep(60)
        TempUsageTraffic.update_temp_usage_of_all_packs()


if RUNNING_SERVER:
    TempUsageTraffic.flush_all()
    threading.Thread(target=check_finished_packs, daemon=True).start()
    init_active_packs_sessions()
    threading.Thread(target=reboot_thread, daemon=True).start()
    threading.Thread(target=update_temp_usage_thread, daemon=True).start()
