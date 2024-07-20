import datetime
import os
import random
import shutil
import socket
import string
import subprocess
import time

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum

from VpnServer.settings import PORTS_START_FROM, EACH_GIG_PRICE
from . import os_user
from .iptables import register_new_chain, get_usage_of_pack_after_startup
from .linux_process_box import kill_all_os_process_of_pack


class Pack(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='packs')
    start_time = models.DateTimeField(blank=True, null=True, default=None)
    days = models.IntegerField(blank=False, null=False)
    linux_username = models.CharField(blank=True, null=True, default='', max_length=10)
    linux_password = models.CharField(blank=True, null=True, default='', max_length=10)
    port = models.IntegerField(default=0, blank=True, null=True)
    started = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    session_pid = models.IntegerField(default=-1, blank=False, null=False)
    specific_ssh_configs = models.TextField(max_length=1000, blank=True, null=False, default='')
    usage = models.IntegerField(default=0, null=False, blank=False)
    label = models.CharField(max_length=1000, default=None, blank=True, null=True)
    free_traffic = models.BooleanField(default=False, null=False, blank=False)
    traffic_limit = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        return self.user.first_name + '-' + 'pack' + str(self.id) + '(' + str(self.days) + ' days)'

    @staticmethod
    def get_first_free_port():
        active_packs = list(Pack.get_active_packs().values('port'))
        packs_ports = [pack['port'] for pack in active_packs]

        def is_port_is_use(port):
            if packs_ports.__contains__(port):
                return True
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('127.0.0.1', port)) == 0

        current_port = PORTS_START_FROM
        while True:
            if not is_port_is_use(current_port):
                break
            current_port += 1
        return current_port

    @staticmethod
    def get_active_packs():
        return Pack.objects.filter(started=True, finished=False)

    def run_pack(self):
        if self.start_time is None:
            self.start_time = datetime.datetime.now()
        self.started = True
        self.finished = False
        if self.linux_username == '' or self.linux_username is None:
            self.linux_username = 'vpn' + str(self.id)
        if self.linux_password == '' or self.linux_password is None:
            letters = string.ascii_lowercase + string.digits
            self.linux_password = ''.join(random.choice(letters) for _ in range(8))
        if self.port is None or self.port == 0:
            self.port = self.get_first_free_port()
        self.save()
        os_user.add_user(self.linux_username, self.linux_password)
        register_new_chain(self)
        self.create_ssh_session()

    def create_ssh_session(self):
        # write ssh config file
        with open('sshd_config', 'r') as file:
            filedata = file.read()
        filedata = filedata.replace('$username$', self.linux_username)
        filedata = filedata.replace('$port$', str(self.port))
        related_ssh_config_file = 'ssh_configs/' + self.linux_username + '_ssh'
        with open(related_ssh_config_file, 'w') as file:
            file.write(filedata)
            file.write('\n' + self.specific_ssh_configs)

        # create ssh session
        command = '/usr/sbin/sshd -f ' + os.path.abspath(related_ssh_config_file)
        os.system(command)

        # calculating pid of ssh session
        command = f"ps aux | grep {self.linux_username}_ssh | head -n 1 | tr -s ' ' | cut -d' ' -f2"
        pid_of_ssh = subprocess.run([command], stdout=subprocess.PIPE, shell=True)
        pid_of_ssh = pid_of_ssh.stdout.decode('utf-8').strip()
        if pid_of_ssh.isnumeric():
            self.session_pid = int(pid_of_ssh)
            self.save()

    def close(self):
        self.started = True
        self.finished = True
        os_user.remove_user(self.linux_username)
        kill_all_os_process_of_pack(self)
        self.usage = UsageTraffic.get_full_traffic_usage_of_pack(self)
        self.save()

    def finish(self):
        self.close()
        self.create_usage_factor()

    def create_usage_factor(self):
        from payment.models import PaymentFactor
        pay_amount = EACH_GIG_PRICE * self.usage / 2 ** 30
        PaymentFactor(related_pack=self, user=self.user, amount=pay_amount,
                      pay_for=PaymentFactor.PayFor.TRAFFIC_USAGE, payed=self.free_traffic).save()

    def connection_count(self):
        command = f"ps ax | grep '{self.linux_username} \[priv\]'"
        result = subprocess.run([command], stdout=subprocess.PIPE, shell=True)
        result = result.stdout.decode('utf-8').strip()
        if result == '':
            return 0
        return len(result.split('\n'))

    def get_usage(self):
        if self.finished:
            return self.usage
        return self.usage + get_usage_of_pack_after_startup(self)

    @staticmethod
    def all_connection_count():
        command = "ps ax | grep ssh | grep '\[priv\]'"
        result = subprocess.run([command], stdout=subprocess.PIPE, shell=True)
        result = result.stdout.decode('utf-8').strip()
        if result == '':
            return 0
        return len(result.split('\n'))


class UsageTraffic(models.Model):
    usage = models.IntegerField(default=0, null=False, blank=False)
    pack = models.ForeignKey(to=Pack, null=False, blank=False, on_delete=models.CASCADE)
    committed = models.BooleanField(default=False)

    @staticmethod
    def update_temp_traffic_usage(pack):
        UsageTraffic.objects.filter(pack=pack, committed=False).delete()
        traffic_after_startup = get_usage_of_pack_after_startup(pack)
        UsageTraffic(pack=pack, usage=traffic_after_startup, committed=False).save()

    @staticmethod
    def get_sum_of_committed_traffics(pack):
        return UsageTraffic.objects.filter(pack=pack, committed=True).aggregate(Sum('usage'))

    @staticmethod
    def commit_all():
        UsageTraffic.objects.filter(committed=False).update(committed=True)

    @staticmethod
    def update_temp_traffic_usage_of_active_packs():
        for pack in Pack.get_active_packs():
            UsageTraffic.update_temp_traffic_usage(pack)

    @staticmethod
    def get_full_traffic_usage_of_pack(pack: Pack):
        traffic_after_startup = get_usage_of_pack_after_startup(pack)
        return UsageTraffic.get_sum_of_committed_traffics(pack) + traffic_after_startup


def check_finished_packs():
    while True:
        for pack in Pack.get_active_packs():
            passed_seconds = (datetime.datetime.now(datetime.timezone.utc) - pack.start_time).total_seconds()
            time_expired = passed_seconds > (pack.days * 24 * 60 * 60)
            traffic_limit_overed = pack.traffic_limit is not None and pack.get_usage() >= pack.traffic_limit
            if time_expired or traffic_limit_overed:
                pack.finish()
        time.sleep(10 * 60)


def init_active_packs_sessions():
    ssh_configs_folder = "ssh_configs"
    if not os.path.exists(ssh_configs_folder):
        os.makedirs(ssh_configs_folder)

    for filename in os.listdir(ssh_configs_folder):
        file_path = os.path.join(ssh_configs_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    for pack in Pack.get_active_packs():
        pack.run_pack()
