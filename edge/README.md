# Mac 2 — Edge reverse proxy

## Team member
Anshvardhan Badkur (`2401010083`) — `Anshvardhans-MacBook-Pro`

## Role
Single client entry: TLS termination, reverse proxy, round-robin load balancing.

## Live inventory
| Field | Value |
|---|---|
| Hostname | `cn-edge` |
| Interface | `en0` |
| IPv4 | `10.7.18.79` |
| HTTP | `8080` |
| HTTPS | `8443` |
| Software | `nginx/1.31.6` |
| Names | `app.team1.test`, `api.team1.test` |
| MAC (shared in lab) | `d6:2c:44:81:38:d2` |

Homebrew nginx on this machine used `include servers/*;`. The working vhost was `/opt/homebrew/etc/nginx/servers/team1.conf`. `nginx.conf.example` in this folder is the full equivalent.

## Upstreams
| Backend | Host | Socket |
|---|---|---|
| A | Ishita / Mac 3 | `10.7.17.218:3001` (was `10.7.11.99:3001`) |
| B | Aditya Verma / Mac 4 | `10.7.31.47:3002` |

On 5 Oct every request went to B until upstream A was changed from the stale `10.7.11.99` to `10.7.17.218`. After `nginx -t` and `brew services restart nginx`, round-robin returned A and B.

## TLS
Certificates were issued with mkcert:

```
/opt/homebrew/etc/nginx/certs/app.team1.test+1.pem
/opt/homebrew/etc/nginx/certs/app.team1.test+1-key.pem
```

Private keys stay on Mac 2. Do not commit them.

## Apply
```bash
brew install nginx
sudo mkdir -p /opt/homebrew/etc/nginx/certs /opt/homebrew/etc/nginx/servers
# generate certs — see tls/README.md
cp edge/nginx.conf.example /opt/homebrew/etc/nginx/nginx.conf
nginx -t
brew services restart nginx
```

## Verify
```bash
curl -i http://localhost:8080/api/status
curl -i --cacert "$(mkcert -CAROOT)/rootCA.pem" \
  --resolve app.team1.test:8443:10.7.18.79 \
  https://app.team1.test:8443/api/status

for i in {1..6}; do
  curl -s -D - http://localhost:8080/api/status -o /dev/null | grep -i X-Backend
done
```

Live mix on 5 Oct after the IP fix:

```
X-Backend: A
X-Backend: A
X-Backend: B
X-Backend: A
X-Backend: B
X-Backend: A
```
