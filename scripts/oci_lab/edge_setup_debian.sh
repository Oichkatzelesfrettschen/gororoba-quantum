#!/bin/sh
# Configure the Debian 13 edge (E2.1.Micro) as the lab router: 2 GB swap,
# IPv4 forwarding, nftables masquerade for the private subnet and WireGuard
# peers leaving the public interface, and a WireGuard server on UDP 51820.
# The WireGuard private key is generated here and never leaves the host.
# OCI security lists filter ingress, so the nftables input chain admits SSH,
# WireGuard and VCN traffic and drops the rest. Run as root; reruns change
# nothing already in place.
set -eu

VCN_CIDR=10.42.0.0/16
WG_CIDR=10.66.0.0/24
WG_ADDR=10.66.0.1/24
WG_PORT=51820

if ! swapon --show | grep -q /swapfile; then
	fallocate -l 2G /swapfile
	chmod 600 /swapfile
	mkswap /swapfile >/dev/null
	swapon /swapfile
	grep -q swapfile /etc/fstab || echo '/swapfile none swap defaults 0 0' >>/etc/fstab
fi

printf 'net.ipv4.ip_forward = 1\nvm.swappiness = 60\n' >/etc/sysctl.d/90-lab.conf
sysctl -q -p /etc/sysctl.d/90-lab.conf

export DEBIAN_FRONTEND=noninteractive
dpkg -s wireguard-tools nftables >/dev/null 2>&1 || {
	apt-get -q update
	apt-get -qy --no-install-recommends install wireguard-tools nftables
}

wan=$(ip -o -4 route show default | awk '{print $5; exit}')
cat >/etc/nftables.conf <<EOF
#!/usr/sbin/nft -f
flush ruleset
table inet lab {
	chain input {
		type filter hook input priority 0; policy drop;
		ct state established,related accept
		iif lo accept
		ip protocol icmp accept
		tcp dport 22 accept
		udp dport $WG_PORT accept
		ip saddr { $VCN_CIDR, $WG_CIDR } accept
		# OCI instance metadata and DHCP replies on the link-local range
		ip saddr 169.254.0.0/16 accept
	}
	chain forward {
		type filter hook forward priority 0; policy drop;
		ct state established,related accept
		ip saddr { $VCN_CIDR, $WG_CIDR } accept
	}
}
table ip lab_nat {
	chain postrouting {
		type nat hook postrouting priority 100;
		oifname "$wan" ip saddr { $VCN_CIDR, $WG_CIDR } ip daddr != $VCN_CIDR masquerade
	}
}
EOF
systemctl enable -q --now nftables
nft -f /etc/nftables.conf

install -d -m 700 /etc/wireguard
if [ ! -f /etc/wireguard/wg0.key ]; then
	umask 077
	wg genkey >/etc/wireguard/wg0.key
	wg pubkey </etc/wireguard/wg0.key >/etc/wireguard/wg0.pub
fi
if [ ! -f /etc/wireguard/wg0.conf ]; then
	umask 077
	printf '[Interface]\nAddress = %s\nListenPort = %s\nPostUp = wg set %%i private-key /etc/wireguard/wg0.key\n' \
		"$WG_ADDR" "$WG_PORT" >/etc/wireguard/wg0.conf
fi
systemctl enable -q --now wg-quick@wg0
echo "edge-setup-done wan=$wan"
