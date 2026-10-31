#!/bin/sh
# Give a Debian 13 lab host a minimal MATE desktop over xrdp. The host sits on
# the private subnet, so RDP (TCP 3389) is reachable only from the VCN and the
# WireGuard range; nftables admits it from those ranges and drops the rest.
# A 2 GB swap file keeps the desktop alive on a 1 GB E2.1.Micro.
# Run as root; reruns change nothing already in place.
set -eu

VCN_CIDR=10.42.0.0/16
WG_CIDR=10.66.0.0/24

if ! swapon --show | grep -q /swapfile; then
	fallocate -l 2G /swapfile
	chmod 600 /swapfile
	mkswap /swapfile >/dev/null
	swapon /swapfile
	grep -q swapfile /etc/fstab || echo '/swapfile none swap defaults 0 0' >>/etc/fstab
fi

export DEBIAN_FRONTEND=noninteractive
dpkg -s mate-desktop-environment-core xrdp >/dev/null 2>&1 || {
	apt-get -q update
	apt-get -qy --no-install-recommends install \
		mate-desktop-environment-core mate-terminal xrdp xorgxrdp dbus-x11 nftables
}
adduser xrdp ssl-cert >/dev/null 2>&1 || true
echo mate-session >/etc/skel/.xsession
for home in /home/*; do
	[ -d "$home" ] || continue
	user=$(basename "$home")
	[ -f "$home/.xsession" ] || install -o "$user" -g "$user" -m 644 /etc/skel/.xsession "$home/.xsession"
done

cat >/etc/nftables.conf <<EOF
#!/usr/sbin/nft -f
flush ruleset
table inet lab {
	chain input {
		type filter hook input priority 0; policy drop;
		ct state established,related accept
		iif lo accept
		ip protocol icmp accept
		ip saddr { $VCN_CIDR, $WG_CIDR } tcp dport { 22, 2049, 3389 } accept
		ip saddr 169.254.0.0/16 accept
	}
}
EOF
systemctl enable -q --now nftables
nft -f /etc/nftables.conf
systemctl enable -q --now xrdp
echo "desktop-setup-done"
