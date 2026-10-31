#!/bin/sh
# Configure lab-edge (Oracle Linux 9 Minimal, E2.1.Micro) as the lab's router:
# IPv4 forwarding, firewalld masquerade from the private subnet and the
# WireGuard range out of the public interface, and a WireGuard server on
# UDP 51820. The private key is generated here and never leaves the host.
# Run as root; reruns change nothing that is already in place.
set -eu

PRIV_CIDR=10.42.1.0/24
WG_CIDR=10.66.0.0/24
WG_ADDR=10.66.0.1/24
WG_PORT=51820

echo 'net.ipv4.ip_forward = 1' >/etc/sysctl.d/90-lab-forward.conf
sysctl -q -p /etc/sysctl.d/90-lab-forward.conf

# dnf's repository metadata for the Oracle Linux 9 repos exceeds 1 GB of
# memory plus 2 GB of swap on an E2.1.Micro and stalls the host, so the
# metadata timer stays off and wireguard-tools installs from the RPM the
# operator copies to /tmp (WG_RPM).
systemctl disable -q --now dnf-makecache.timer
rpm -q wireguard-tools >/dev/null 2>&1 || rpm -i "${WG_RPM:-/tmp/wireguard-tools.rpm}"

# The public zone masquerades traffic leaving ens3; the trusted zone admits
# the private subnet and WireGuard peers, so forwarding between them is open.
firewall-cmd -q --permanent --zone=public --add-masquerade
firewall-cmd -q --permanent --zone=public --add-port="$WG_PORT/udp"
firewall-cmd -q --permanent --zone=trusted --add-source="$PRIV_CIDR"
firewall-cmd -q --permanent --zone=trusted --add-interface=wg0
firewall-cmd -q --reload

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
echo "edge-setup-done wg-pub=$(cat /etc/wireguard/wg0.pub) wg-cidr=$WG_CIDR"
