# Evidence Index — Team Snorlax

Live verification captures from the physical macOS nodes during the 1 Oct 2026 and 5 Oct 2026 laboratory working sessions.

## Evidence Summary Table

| Category | File Path | Description & Observed Output |
|:---|:---|:---|
| **Setup** | [`evidence/setup/Mac1-Firewall-dnsmasq-node.png`](setup/Mac1-Firewall-dnsmasq-node.png) | macOS Application Firewall showing incoming connections explicitly allowed for `dnsmasq` and `node`. |
| **Setup** | [`evidence/setup/Mac1-dnsmasq-firewall.jpg`](setup/Mac1-dnsmasq-firewall.jpg) | Mac 1 terminal demonstrating firewall adjustments for socket port 53. |
| **Setup** | [`evidence/setup/Mac2-certs-dir.jpg`](setup/Mac2-certs-dir.jpg) | Mac 2 directory listing of `/opt/homebrew/etc/nginx/certs` with mkcert certificates. |
| **Setup** | [`evidence/setup/Mac2-nginx-conf-default.jpg`](setup/Mac2-nginx-conf-default.jpg) | Initial Nginx configuration state before reverse proxy virtual host creation. |
| **Task A** | [`evidence/task-a/Mac1-TaskA-dnsmasq-listen.png`](task-a/Mac1-TaskA-dnsmasq-listen.png) | `dnsmasq` started on Mac 1, listening on `10.7.19.196:53`, verified with local `dig`. |
| **Task B** | [`evidence/task-b/Mac1-TaskB-dnsmasq-config.png`](task-b/Mac1-TaskB-dnsmasq-config.png) | Active `dnsmasq.conf` showing `listen-address=10.7.19.196` and `address=/app.team1.test/10.7.18.79`. |
| **Task B** | [`evidence/task-b/Mac1-TaskB-DNS-Resolution.png`](task-b/Mac1-TaskB-DNS-Resolution.png) | `dig @10.7.19.196 app.team1.test +short` returning `10.7.18.79`. |
| **Task B** | [`evidence/task-b/Mac3-TaskB-nslookup.jpg`](task-b/Mac3-TaskB-nslookup.jpg) | Remote resolution: Mac 3 client querying `10.7.19.196` via `nslookup` successfully resolving `10.7.18.79`. |
| **Task B** | [`evidence/task-b/Mac3-TaskB-dig-via-team-dns.jpg`](task-b/Mac3-TaskB-dig-via-team-dns.jpg) | Mac 3 querying team DNS via `dig`, receiving authoritative `NOERROR` answer `10.7.18.79`. |
| **Task C** | [`evidence/task-c/Mac2-TaskC-Direct-Backends.jpg`](task-c/Mac2-TaskC-Direct-Backends.jpg) | Direct backend verification from Mac 2: `curl -i http://10.7.17.218:3001` (A) and `http://10.7.31.47:3002` (B). |
| **Task C** | [`evidence/task-c/Mac3-TaskC-BackendA-node-server.jpg`](task-c/Mac3-TaskC-BackendA-node-server.jpg) | Node.js Express server running on Mac 3 port 3001 with `X-Backend: A`. |
| **Task C** | [`evidence/task-c/Mac4-TaskC-BackendB-python-app.jpg`](task-c/Mac4-TaskC-BackendB-python-app.jpg) | Python Flask / Werkzeug server running on Mac 4 port 3002 with `X-Backend: B`. |
| **Task D** | [`evidence/task-d/Mac2-TaskD-HTTPS-LoadBalancing.jpg`](task-d/Mac2-TaskD-HTTPS-LoadBalancing.jpg) | Mac 2 curl loop against HTTPS `:8443` demonstrating alternating `X-Backend: A` and `B`. |
| **Task D** | [`evidence/task-d/Mac3-TaskD-LoadBalancing.jpg`](task-d/Mac3-TaskD-LoadBalancing.jpg) | Mac 3 10-request loop against `https://app.team1.test:8443` proving balanced round-robin. |
| **Task D** | [`evidence/task-d/Mac4-TaskD-LoadBalancing.jpg`](task-d/Mac4-TaskD-LoadBalancing.jpg) | Mac 4 executing test loop validating both backends serve traffic. |
| **Task E** | [`evidence/task-e/Mac2-TaskE-mkcert-HTTPS.jpg`](task-e/Mac2-TaskE-mkcert-HTTPS.jpg) | mkcert SAN certificate active on Nginx, serving HTTP/2 over TLS 1.3 on port 8443. |
| **Task E** | [`evidence/task-e/Mac3-TaskE-HTTPS.jpg`](task-e/Mac3-TaskE-HTTPS.jpg) | Remote trusted HTTPS curl from Mac 3 returning `HTTP/2 200` without `-k`. |
| **Task F** | [`evidence/task-f/Mac2-TaskF-Cache-ETag.jpg`](task-f/Mac2-TaskF-Cache-ETag.jpg) | Response headers showing `Cache-Control: max-age=60` and `ETag: W/"1d-..."`. |
| **Task F** | [`evidence/task-f/Mac4-TaskF-304-via-nginx.jpg`](task-f/Mac4-TaskF-304-via-nginx.jpg) | Conditional request with `If-None-Match: "v1"` returning `HTTP/1.1 304 NOT MODIFIED`. |
| **Task F** | [`evidence/task-f/Mac4-TaskF-Cache-200-and-304.jpg`](task-f/Mac4-TaskF-Cache-200-and-304.jpg) | Side-by-side verification: initial fetch returns 200, conditional fetch returns 304. |
| **Task G** | [`evidence/task-g/Mac3-TaskG-DNS-Query-Response.jpg`](task-g/Mac3-TaskG-DNS-Query-Response.jpg) | **Wireshark Capture**: Frames 3266 & 3271 showing DNS query for `app.team1.test` and answer `10.7.18.79`. |
| **Task G** | [`evidence/task-g/Mac3-TaskG-TCP-TLS-Handshake.jpg`](task-g/Mac3-TaskG-TCP-TLS-Handshake.jpg) | **Wireshark Capture**: Frames 3273-3281 showing TCP 3-way handshake (`SYN`/`SYN-ACK`/`ACK`) & TLS ClientHello (SNI) / ServerHello. |
| **Task G** | [`evidence/task-g/CNPhase1_Wireshark_Capture.pcapng`](task-g/CNPhase1_Wireshark_Capture.pcapng) | Complete raw Wireshark pcapng capture file containing 11,365 recorded frames. |
