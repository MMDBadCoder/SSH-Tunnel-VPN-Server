import os
import threading
from time import sleep

from django.core.wsgi import get_wsgi_application

from VpnServer.settings import RUNNING_SERVER, UPDATE_TEMP_TRAFFIC_USAGE_SECONDS
from packs.models import check_finished_packs, init_active_packs_sessions, UsageTraffic

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VpnServer.settings')

application = get_wsgi_application()


def update_temp_usage_thread():
    while True:
        sleep(UPDATE_TEMP_TRAFFIC_USAGE_SECONDS)
        UsageTraffic.update_temp_traffic_usage_of_active_packs()


if RUNNING_SERVER:
    UsageTraffic.commit_all()
    threading.Thread(target=check_finished_packs, daemon=True).start()
    init_active_packs_sessions()
    threading.Thread(target=update_temp_usage_thread, daemon=True).start()
