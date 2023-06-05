import subprocess


def create_chain_name(pack):
    return 'vpn-chain-' + str(pack.id)


def register_new_chain(pack):
    if get_usage_of_pack_after_startup(pack) != 0:
        return
    chain_name = create_chain_name(pack)
    command = f"iptables -N {chain_name}"
    subprocess.run([command], shell=True)
    command = f'iptables -A INPUT -p tcp --dport {pack.port} -j {chain_name}'
    subprocess.run([command], shell=True)
    command = f'iptables -A OUTPUT -p tcp --sport {pack.port} -j {chain_name}'
    subprocess.run([command], shell=True)


def get_usage_of_pack_after_startup(pack):
    chain_name = create_chain_name(pack)
    command = F'iptables -L -n -v | grep \' {chain_name} \' | head -n 2 | tr -s \' \''
    command_output = subprocess.run([command], stdout=subprocess.PIPE, shell=True)
    command_output = command_output.stdout.decode('utf-8').strip()

    if command_output == '':
        return 0

    total_usage = 0

    for line in command_output.split('\n'):
        line = line.strip()
        usage_part = line.split(' ')[1]
        usage_part = usage_part.replace('K', '000').replace('M', '000000').replace('G', '000000000')
        if usage_part.isnumeric():
            total_usage += int(usage_part)

    return total_usage
