# Cluster Setup and Deployment Runbook

## Computer Networks Capstone: Private Network Service Platform — Team Baby Shark

### Core Principle
> "The application stays simple; the network is the project."

This guide walks through configuring each of the four physical macOS laptops from a fresh state to a fully operating distributed cluster.

---

## 1. Prerequisites Across All Nodes

Verify common dependencies on all four machines:
```bash
# Verify Homebrew installation
brew --version

# Verify curl and dig
curl --version
dig -v
```

---

## 2. Mac 1 Setup: Private DNS Server (Yug Johri)

### Step 2.1: Install dnsmasq
```bash
brew install dnsmasq
sudo mkdir -p /opt/homebrew/etc/dnsmasq.d
```

### Step 2.2: Deploy Configuration Files
Copy `dns/dnsmasq.conf.example` to `/opt/homebrew/etc/dnsmasq.conf`:
```conf
listen-address=10.7.19.196,127.0.0.1
bind-interfaces
server=8.8.8.8
log-queries
log-facility=/tmp/dnsmasq.log
conf-dir=/opt/homebrew/etc/dnsmasq.d/,*.conf
```

Copy `dns/project.conf.example` to `/opt/homebrew/etc/dnsmasq.d/project.conf`:
```conf
address=/app.team1.test/10.7.18.79
address=/api.team1.test/10.7.18.79
local-ttl=30
```

### Step 2.3: Configure macOS Firewall
Ensure `dnsmasq` is permitted to receive incoming UDP/TCP port 53 traffic:
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /opt/homebrew/opt/dnsmasq/sbin/dnsmasq
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /opt/homebrew/opt/dnsmasq/sbin/dnsmasq
```

### Step 2.4: Start dnsmasq Service
```bash
sudo /opt/homebrew/opt/dnsmasq/sbin/dnsmasq --test --conf-file=/opt/homebrew/etc/dnsmasq.conf
sudo brew services start dnsmasq
sudo lsof -nP -iUDP:53 -iTCP:53
```

### Step 2.5: Verify DNS Resolution
```bash
dig @10.7.19.196 app.team1.test +short
# Expected output: 10.7.18.79
```

---

## 3. Mac 2 Setup: Edge Proxy & TLS Termination (Anshvardhan Badkur)

### Step 3.1: Install Nginx and mkcert
```bash
brew install nginx mkcert nss
mkcert -install
```

### Step 3.2: Issue SAN TLS Certificates
```bash
sudo mkdir -p /opt/homebrew/etc/nginx/certs /opt/homebrew/etc/nginx/servers
cd /opt/homebrew/etc/nginx/certs
mkcert app.team1.test api.team1.test
# Creates: app.team1.test+1.pem and app.team1.test+1-key.pem
```

### Step 3.3: Deploy Virtual Host Configuration
Create `/opt/homebrew/etc/nginx/servers/team1.conf`:
```nginx
upstream backend_pool {
    server 10.7.17.218:3001;
    server 10.7.31.47:3002;
}

server {
    listen 8080;
    server_name app.team1.test api.team1.test;

    location / {
        proxy_pass http://backend_pool;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_next_upstream error timeout http_502 http_503 http_504;
    }
}

server {
    listen 8443 ssl;
    http2 on;
    server_name app.team1.test api.team1.test;

    ssl_certificate     /opt/homebrew/etc/nginx/certs/app.team1.test+1.pem;
    ssl_certificate_key /opt/homebrew/etc/nginx/certs/app.team1.test+1-key.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://backend_pool;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_next_upstream error timeout http_502 http_503 http_504;
    }
}
```

### Step 3.4: Test and Start Nginx
```bash
nginx -t
brew services restart nginx
```

---

## 4. Mac 3 Setup: Backend A Server (Ishita Thakur)

### Step 4.1: Install Node.js Dependencies and Start Server
```bash
cd backend-a
npm install
npm start
```
Binds to `0.0.0.0:3001`.

### Step 4.2: Firewall Configuration
Ensure Node.js is allowed incoming network connections:
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$(which node)"
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$(which node)"
```

### Step 4.3: Local Verification
```bash
curl -i http://localhost:3001/api/status
```

---

## 5. Mac 4 Setup: Backend B Server (Aditya Verma)

### Step 5.1: Install Dependencies and Start Python Server
```bash
cd backend-b
python3 -m pip install -r requirements.txt
python3 app.py
```
Binds to `0.0.0.0:3002`.

### Step 5.2: Local Verification
```bash
curl -i http://localhost:3002/api/status
curl -i http://localhost:3002/api/cached
curl -i -H 'If-None-Match: "v1"' http://localhost:3002/api/cached
# HTTP/1.1 304 NOT MODIFIED
```

---

## 6. Client Node Setup (Mac 1 / Mac 4)

Configure DNS resolver pointing to Mac 1:
```bash
sudo networksetup -setdnsservers Wi-Fi 10.7.19.196
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

Run test suite:
```bash
./tests/dns-test.sh
./tests/https-test.sh
./tests/load-balancing-test.sh
./tests/caching-test.sh
```
