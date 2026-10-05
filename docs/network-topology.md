# Network Topology and Addressing Specification

## Computer Networks Capstone: Private Network Service Platform — Team Baby Shark

### Subnet Overview
- **Network CIDR**: `10.7.0.0/16` (Campus Private Wi-Fi LAN)
- **Active Interface**: `en0` on all physical macOS nodes
- **Broadcast Domain**: Shared Class A local area network

---

## 1. Physical Node Addressing Matrix

| Node | Machine Role | Assigned IPv4 | MAC Address | Open Ports / Protocol | Primary Process |
|:---|:---|:---|:---|:---|:---|
| **Mac 1 (Yug)** | Authoritative DNS | `10.7.19.196` | Verified via `ifconfig` | `53/udp`, `53/tcp` | `dnsmasq 2.93` |
| **Mac 2 (Ansh)** | Edge Proxy & TLS | `10.7.18.79` | `d6:2c:44:81:38:d2` | `8080/tcp`, `8443/tcp` | `nginx 1.31.6` |
| **Mac 3 (Ishita)** | Backend A Origin | `10.7.17.218` | Verified via `ifconfig` | `3001/tcp` | Node.js Express |
| **Mac 4 (Aditya)** | Backend B Origin | `10.7.31.47` | Verified via `ifconfig` | `3002/tcp` | Python Flask |

*Note on Mac 3 DHCP*: During the initial lab session on 1 Oct, Mac 3 held IP `10.7.11.99`. On 5 Oct, campus DHCP reassigned it to `10.7.17.218`. The Nginx upstream on Mac 2 was updated accordingly.

---

## 2. End-to-End Packet Traversal Flow

```
+-----------------------------------------------------------------------------+
|                               CAMPUS WI-FI LAN                              |
|                                 10.7.0.0/16                                 |
+-----------------------------------------------------------------------------+
         |                                                   |
         |  [1] DNS Query (UDP 53)                           |  [2] DNS Response
         |      app.team1.test?                              |      10.7.18.79
         v                                                   v
+-------------------------+                         +-------------------------+
|     MAC 1 (cn-dns)      |                         |       CLIENT NODE       |
|    10.7.19.196:53       |                         |      (Mac 1 / Mac 4)    |
+-------------------------+                         +-------------------------+
                                                                 |
         +-------------------------------------------------------+
         |
         | [3] TCP 3-Way Handshake (SYN -> SYN-ACK -> ACK) to 10.7.18.79:8443
         | [4] TLS 1.2/1.3 Handshake (ClientHello -> ServerHello -> Cert -> Finished)
         | [5] Encrypted HTTPS Request (GET /api/status)
         v
+-----------------------------------------------------------------------------+
|                               MAC 2 (cn-edge)                               |
|                            10.7.18.79:8080 / :8443                          |
|                       Nginx Reverse Proxy & Load Balancer                   |
+-----------------------------------------------------------------------------+
         |                                                   |
         | [6a] HTTP/1.1 (Round-Robin Turn 1)                | [6b] HTTP/1.1 (Turn 2)
         v                                                   v
+-------------------------+                         +-------------------------+
|   MAC 3 (cn-backend-a)  |                         |   MAC 4 (cn-backend-b)  |
|    10.7.17.218:3001     |                         |     10.7.31.47:3002     |
|   Node.js Express       |                         |    Python Flask         |
|   X-Backend: A          |                         |    X-Backend: B         |
+-------------------------+                         +-------------------------+
         |                                                   |
         +-------------------------+-------------------------+
                                   |
                                   | [7] HTTP 200 OK + Payload
                                   v
+-----------------------------------------------------------------------------+
|                               MAC 2 (cn-edge)                               |
|                       Encapsulate in Active TLS Session                     |
+-----------------------------------------------------------------------------+
                                   |
                                   | [8] HTTP/2 200 OK (TLS encrypted)
                                   v
+-----------------------------------------------------------------------------+
|                                 CLIENT NODE                                 |
+-----------------------------------------------------------------------------+
```
