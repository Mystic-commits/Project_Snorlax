# Comprehensive Team Viva Voce Revision Guide

## Computer Networks Capstone: Private Network Service Platform — Team Snorlax

---

## 1. Yug Johri — Mac 1 (Private DNS Resolver Specialist)
*Enrollment: `2401010520` | Hostname: `cn-dns` | IP: `10.7.19.196`*

### Core Theoretical Questions

1. **What is the difference between an Authoritative and Recursive DNS server?**
   - **Authoritative DNS**: Holds the actual DNS database records for a zone (e.g., `address=/app.team1.test/10.7.18.79`) and provides conclusive answers for queries within that domain.
   - **Recursive DNS**: Traverses the root, TLD, and authoritative name servers on behalf of a client to resolve unknown domain names.
   - In our project, `dnsmasq` serves as an authoritative resolver for our private `.test` zone and acts recursively for public queries by upstream forwarding to `8.8.8.8`.

2. **Why was `.test` chosen instead of `.local` or `.dev`?**
   - RFC 6762 explicitly reserves `.local` for Multicast DNS (mDNS/Bonjour). On macOS, queries ending in `.local` are intercepted by the OS kernel and broadcast over multicast IP `224.0.0.251` on port 5353, breaking unicast DNS resolution.
   - RFC 2606 and RFC 6761 reserve `.test` specifically for testing and isolated networks, preventing public conflict.

3. **What is the transport difference between UDP port 53 and TCP port 53 in DNS?**
   - Standard DNS lookups use UDP 53 for minimum latency and connectionless speed.
   - DNS switches to TCP 53 when a response packet exceeds 512 bytes (or client EDNS0 buffer sizes) indicated by the TrunCation (`TC`) bit, or during DNS Zone Transfers (AXFR).

4. **Why did we set `local-ttl=30`?**
   - A short 30-second TTL prevents intermediate caches and client resolver daemons (`mDNSResponder`) from holding stale IP mappings during simulated failovers or IP reassignments.

---

## 2. Anshvardhan Badkur — Mac 2 (Edge Proxy, Load Balancer & Security Specialist)
*Enrollment: `2401010083` | Hostname: `cn-edge` | IP: `10.7.18.79`*

### Core Theoretical Questions

1. **What is the difference between a Reverse Proxy and a Forward Proxy?**
   - **Forward Proxy**: Sits in front of clients, inspects outbound traffic, hides client IP addresses, and accesses the internet on the client's behalf.
   - **Reverse Proxy**: Sits in front of backend origin servers, intercepts all inbound client connections, terminates TLS, load-balances requests, and shields the internal server topology and IPs from clients.

2. **How does TLS Termination operate at the edge?**
   - The cryptographic handshake terminates on Mac 2 using the server private key (`app.team1.test+1-key.pem`). Nginx decrypts the incoming HTTPS traffic into plain HTTP/1.1 and proxies it across the internal LAN to Mac 3 and Mac 4. This offloads compute-heavy asymmetric cryptography from backend origins.

3. **Why is Server Name Indication (SNI) essential?**
   - In standard TLS, the handshake occurs before any HTTP headers (such as `Host: app.team1.test`) are sent. SNI is an extension to TLS that allows the client to include the requested hostname inside the initial `ClientHello` record. This allows Nginx to select the correct virtual host and X.509 certificate on a single IP address.

4. **How does Round-Robin load balancing handle dead backend nodes?**
   - By default, Nginx distributes requests sequentially between upstream servers (`backend_pool`).
   - With `proxy_next_upstream error timeout http_502 http_503 http_504;`, if a backend returns a 502 Bad Gateway or connection timeout, Nginx immediately reroutes the pending request to the next available upstream before responding to the client, providing automatic fault tolerance.

---

## 3. Ishita Thakur — Mac 3 (Backend Application Server A Specialist)
*Hostname: `cn-backend-a` | IP: `10.7.17.218` (was `10.7.11.99`)*

### Core Theoretical Questions

1. **What is an ETag and how does conditional caching work?**
   - An ETag (Entity Tag) is an HTTP response header that acts as a fingerprint for a specific version of a resource.
   - When a client issues a subsequent request with `If-None-Match: <etag>`, the server checks if the resource is unchanged. If identical, the server responds with `HTTP 304 Not Modified` with zero body bytes, saving significant network bandwidth and server latency.

2. **Why must backend servers bind to `0.0.0.0` instead of `127.0.0.1`?**
   - `127.0.0.1` is the loopback interface (`lo0`), which only accepts connections originating from processes running locally on the same physical computer.
   - Binding to `0.0.0.0` (all IPv4 interfaces) instructs the kernel socket to accept connections from external hosts on the physical network interface (`en0`), allowing Mac 2 (`10.7.18.79`) to connect to port 3001.

3. **What happened when your machine's IP address changed via DHCP?**
   - Node.js code did not require any change because it bound to `0.0.0.0:3001`.
   - However, Nginx on Mac 2 maintained upstream socket target `10.7.11.99:3001`. Because the new IP was `10.7.17.218`, Nginx could no longer route packets to Backend A, causing all traffic to fail over to Backend B until Nginx upstream configuration was updated.

---

## 4. Aditya Verma — Mac 4 (Backend B & Network Testing Specialist)
*Enrollment: `2401010040` | Hostname: `cn-backend-b` | IP: `10.7.31.47`*

### Core Theoretical Questions

1. **What is a 4-tuple TCP socket pair?**
   - A TCP connection is uniquely identified across an entire network by the socket 4-tuple:
     `{Source IP, Source Port, Destination IP, Destination Port}`.
   - For example: `{10.7.31.47, 52194, 10.7.18.79, 8443}`.

2. **What is the difference between Well-Known, Registered, and Ephemeral ports?**
   - **Well-Known Ports (0–1023)**: Reserved for core privileged services (e.g., DNS on 53, HTTP on 80).
   - **Registered Ports (1024–49151)**: Assigned to user services and applications (e.g., Node on 3001, Python on 3002, Nginx on 8080/8443).
   - **Ephemeral Ports (49152–65535 on macOS)**: Dynamically allocated by the client OS kernel for outbound sockets during request execution.

3. **Explain the TCP Three-Way Handshake step-by-step as captured in Wireshark.**
   - **Step 1 (SYN)**: Client sends TCP packet with `SYN=1`, random initial sequence number `ISN_c`, advertising MSS.
   - **Step 2 (SYN-ACK)**: Server responds with `SYN=1`, `ACK=1`, acknowledging `ISN_c + 1` and providing server sequence number `ISN_s`.
   - **Step 3 (ACK)**: Client responds with `ACK=1`, acknowledging `ISN_s + 1`. Socket state transitions to `ESTABLISHED`.
