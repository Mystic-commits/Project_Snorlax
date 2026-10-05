# TLS termination

HTTPS ends at nginx on Mac 2 (`10.7.18.79:8443`). Backends speak plain HTTP on the LAN.

## Live lab
The edge used **mkcert** SAN certs, not a raw OpenSSL self-signed pair:

```
app.team1.test+1.pem
app.team1.test+1-key.pem
```

Clients that trust the mkcert CA can call HTTPS without `-k`:

```bash
curl -i --cacert "$(mkcert -CAROOT)/rootCA.pem" \
  --resolve app.team1.test:8443:10.7.18.79 \
  https://app.team1.test:8443/api/status
```

Verified: `HTTP/2 200`, `server: nginx/1.31.6`, `x-backend: A` or `B`.

## mkcert (what we ran)
```bash
brew install mkcert nss
mkcert -install
sudo mkdir -p /opt/homebrew/etc/nginx/certs
cd /opt/homebrew/etc/nginx/certs
mkcert app.team1.test api.team1.test
```

## OpenSSL alternative
If mkcert is unavailable:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -config tls/openssl.cnf.example \
  -keyout /opt/homebrew/etc/nginx/certs/server.key \
  -out /opt/homebrew/etc/nginx/certs/server.crt

openssl x509 -in /opt/homebrew/etc/nginx/certs/server.crt \
  -noout -subject -issuer -dates -ext subjectAltName
```

Then point `ssl_certificate` / `ssl_certificate_key` at those files.

Trust on a client:

```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain server.crt
```

Final demo curl must not use `-k` / `--insecure`.

## Never commit
`*.pem`, `*.key`, and `*.crt` are gitignored. Only Mac 2 holds the private key.
