username="--username--"
password="--password--"
ip="--ip--"
port="--port--"

scp -rp -P "$port" ./archive "$username"@"$ip":~/
ssh "$username"@"$ip" -p "$port" -f "bash ~/archive/install.sh"
