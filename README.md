# SSH-Tunnel-VPN-Server

full automated vpn server

<h3>Instructions to deploy vpn server</h3>
<ol>
<li>Clone code by <code>sudo apt install git ; git clone https://github.com/MMDBadCoder/SSH-Tunnel-VPN-Server.git</code></li>
<li>Go to project's Directory by <code>cd SSH-Tunnel-VPN-Server/</code></li>
<li>Tune your customized settings in VpnServer/settings by <code>vim VpnServer/settings.py</code></li>
<li>Install MMD-VPN by <code>bash install.sh</code></li>
<li>Add your webhook address to Idpay webhook field, idpay webhook should be filled by <code>yourhost/payment/webhook</code></li>
</ol>

<h3>Features</h3>
<ul>
    <li>Simple user interface</li>
    <li>Connecting to idpay</li>
    <li>Android + Windows + Linux</li>
    <li>Full automation</li>
</ul>

<h4>Admin access</h4>
<ul>
    <li>Admin panel is on <code>hostname/admin</code></li>
    <li>MMD-VPN works with a linux systemd service, and admin can start/stop it by systemctl commands.
for example, admin can restart it by <code>sudo systemctl restart mmdvpn</code></li>
<li>Admin can add new superuser by executing <code>./adduser.sh</code></li>
<li>Admin can run server manually by executing <code>./runserver.sh</code></li>
<li>Admin can monitor active sessions in <code>/active</code> url</li>
</ul>