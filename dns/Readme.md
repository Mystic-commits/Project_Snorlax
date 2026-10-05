# Mac 1 — Private DNS

## Team member
Yug Johri (`2401010520`) — `Yugs-MacBook-Pro-3`

## Role
Authoritative resolver for `app.team1.test` and `api.team1.test`, plus a test client (`dig`, `nslookup`, `curl`, Wireshark).

## Live inventory
| Field | Value |
|---|---|
| Hostname | `cn-dns` |
| Interface | `en0` |
| IPv4 | `10.7.19.196` |
| Service | `dnsmasq 2.93` |
| Port | `53/udp` and `53/tcp` |
| Zone | `.test` |
| A records | `app.team1.test` → `10.7.18.79` |
| | `api.team1.test` → `10.7.18.79` |

`10.7.18.79` is Mac 2 (nginx).

## Why `.test`
macOS intercepts `.local` with Bonjour / mDNSResponder (`224.0.0.251`). `.test` stays unicast DNS.

## Install
```bash
brew install dnsmasq
sudo mkdir -p "$(brew --prefix)/etc/dnsmasq.d"
sudo cp dns/dnsmasq.conf.example "$(brew --prefix)/etc/dnsmasq.conf"
sudo cp dns/project.conf.example "$(brew --prefix)/etc/dnsmasq.d/project.conf"
```

Update `listen-address` if Mac 1 DHCP changes.

## Start
```bash
sudo "$(brew --prefix)/opt/dnsmasq/sbin/dnsmasq" --test --conf-file="$(brew --prefix)/etc/dnsmasq.conf"
sudo brew services start dnsmasq
sudo lsof -nP -iUDP:53 -iTCP:53
```

Allow `/opt/homebrew/opt/dnsmasq/sbin/dnsmasq` through Application Firewall. On 1 Oct the firewall blocked LAN DNS until that rule existed.

## Client machines
```bash
sudo networksetup -setdnsservers Wi-Fi 10.7.19.196
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

If a client still uses `8.8.8.8`, `dig app.team1.test` returns NXDOMAIN from the public roots.

## Verify
```bash
dig @10.7.19.196 app.team1.test +short
# 10.7.18.79

dig @10.7.19.196 api.team1.test +short
nslookup app.team1.test 10.7.19.196
ping -c 3 app.team1.test
```

Verified on Mac 1 and Mac 3 (Ishita): `SERVER: 10.7.19.196#53`, answer `10.7.18.79`.
