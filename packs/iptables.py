import subprocess


def create_chain_name(pack):
    return 'vpn-chain-' + str(pack.id)


def register_new_chain(pack):
    chain_name = create_chain_name(pack)
    command = f"iptables -N {chain_name}"
    subprocess.run([command], shell=True)
    command = f'iptables -A INPUT -p tcp --dport {pack.port} -j {chain_name}'
    subprocess.run([command], shell=True)


def get_usage_of_pack_after_startup(pack):
    chain_name = create_chain_name(pack)
    command = F'iptables -L -n -v | grep {chain_name} | head -n 1 | tr -s ' ' | cut -d' ' -f3'
    usage = subprocess.run([command], stdout=subprocess.PIPE, shell=True)
    usage = usage.stdout.decode('utf-8').strip()
    if usage.isnumeric():
        return int(usage)
    return 0
