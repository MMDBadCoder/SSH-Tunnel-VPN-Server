# SSH-Tunnel-VPN-Server

full automated vpn server

<h3>Instructions to deploy vpn server</h3>
<ol>
    <li>Install <code>ufw</code> by this command:
    <code>sudo apt install ufw</code>
    </li>
    <li>Allow your vpn ports, and your specific root ssh port
    by this commands:
        <br>
        <code>sudo ufw allow 2200:2230/tcp</code>
        <br>
        <code>sudo ufw allow 2200:2230/udp</code>
        <br>
        for your ssh: <code>sudo ufw allow 2280</code>
        <br>
        for server ui: <code>sudo ufw allow 80</code> 
</li>
<li>Enable ufw by <code>sudo ufw enable</code></li>
<li>Clone code by <code>sudo apt install git ; git clone https://github.com/MMDBadCoder/SSH-Tunnel-VPN-Server.git</code></li>
<li>Go to project's Directory by <code>cd SSH-Tunnel-VPN-Server/</code></li>
<li>Tune your customized settings in VpnServer/settings by <code>vim VpnServer/settings.py</code></li>
<li>Install MMD-VPN by <code>chmod +x install.sh ; ./install.sh</code></li>
<li>Add your webhook address to Idpay webhook field, idpay webhook should be filled by <code>yourhost/payment/webhook</code></li>
</ol>

<h3>Features</h3>
<ul>
    <li>Simple user interface</li>
    <li>Connecting to idpay</li>
    <li>Android + Windows</li>
    <li>Full automation</li>
</ul>

<h4>Admin access</h4>
<ul>
    <li>Admin panel is on <code>hostname/admin</code></li>
    <li>MMD-VPN works with a linux systemd service, and admin can start/stop it by systemctl commands.
for example, admin can restart it by <code>sudo systemctl restart mmdvpn</code></li>
<li>Admin can add new superuser by executing <code>./adduser.sh</code></li>
<li>Admin can run server manually by executing <code>./runserver.sh</code></li>
</ul>