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

from VpnServer.settings import PORTS_START_FROM
from . import os_user


class Pack(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='packs')
    start_time = models.DateTimeField(blank=True, null=True, default=None)
    days = models.IntegerField(blank=False, null=False)
    linux_username = models.CharField(blank=True, null=True, default='', max_length=10)
    linux_password = models.CharField(blank=True, null=True, default='', max_length=10)
    port = models.IntegerField(default=0, blank=True, null=True)
    started = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + '-' + 'pack' + str(self.id) + '(' + str(self.days) + ' days)'

    @staticmethod
    def get_first_free_port():
        packs_ports = Pack.objects.filter(started=True, finished=False).values_list('port')

        def is_port_is_use(port):
            if packs_ports.contains(port):
                return True
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('127.0.0.1', port)) == 0

        current_port = PORTS_START_FROM
        while True:
            if not is_port_is_use(current_port):
                break
            current_port += 1
        return current_port

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

        # create ssh session
        command = '/usr/sbin/sshd -f ' + os.path.abspath(related_ssh_config_file)
        os.system(command)

        # open port by ufw
        subprocess.call(['ufw', 'allow', str(self.port)])

    def finish(self):
        self.started = True
        self.finished = True
        self.save()
        os_user.remove_user(self.linux_username)

        # getting pid of ssh session and kill process
        command = f"ps aux | grep {self.linux_username}_ssh | head -n 1 | tr -s ' ' | cut -d' ' -f2"
        pid_of_ssh = subprocess.run([command], stdout=subprocess.PIPE, shell=True)
        pid_of_ssh = pid_of_ssh.stdout.decode('utf-8').strip()
        if pid_of_ssh is not None and pid_of_ssh.isnumeric() and int(pid_of_ssh) != 0:
            try:
                os.kill(int(pid_of_ssh), 9)
                print(f"Pack {self.id} was finished successfully.")
            except Exception as e:
                print(f"Failed at finishing pack {self.id}")
                print(e)

        # close session port by ufw
        subprocess.call(['ufw', 'deny', str(self.port)])


def check_finished_packs():
    while True:
        time.sleep(60 * 60)
        for pack in Pack.objects.filter(started=True, finished=False):
            passed_seconds = (datetime.datetime.now(datetime.timezone.utc) - pack.start_time).total_seconds()
            if passed_seconds > (pack.days * 24 * 60 * 60):
                pack.finish()


def init_sshd_services():
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

    for pack in Pack.objects.filter(started=True, finished=False):
        pack.run_pack()
