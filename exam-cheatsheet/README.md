# EE6011 Lab Exam Cheat Sheet: Labs 2, 3 and 6

Open book notes for the GNS3 lab exam. Commands are paste-ready. Paste one router at a time, check the window title first, and paste the commands only, never the `R1(config-if)#` prompt text.

## Always do this

1. Set the router slots before starting the routers. A missing module means a missing interface (`Invalid input` on `interface s1/0` or `g1/0`).
   - Lab 2: default `C7200-IO-2FE`
   - Lab 3: slot 0 `C7200-IO-FE`, slot 1 `PA-4T+` (gives s1/0)
   - Lab 6: slot 0 `C7200-IO-FE`, slot 1 `PA-GE`, slot 2 `PA-GE` (gives g1/0 and g2/0)
2. Start the Wireshark capture on the link before applying the thing you want to capture (right-click the link, Start capture).
3. First ping after any VPN change often times out. Ping again.
4. At the end: `write memory` on every router (Enter at the overwrite prompt), `save` on every PC, stop all devices, File > Export portable project, name it with your ID number.
5. If a VPN or auth link fails, compare both ends: `show run | section crypto` (or `show run interface g1/0`). The cause is nearly always a mismatch, a missing line or a wrong ACL.

## Lab 2: IPSec site-to-site VPN

Topology: PC1 (192.168.1.2) - R1 f0/0 192.168.1.1, R1 f0/1 10.0.0.1/30 - R2 f0/1 10.0.0.2/30, R2 f0/0 192.168.2.1 - PC2 (192.168.2.2).

### Base config
```
PC1> ip 192.168.1.2/24 192.168.1.1
PC2> ip 192.168.2.2/24 192.168.2.1

R1
conf t
interface f0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface f0/1
 ip address 10.0.0.1 255.255.255.252
 no shutdown
exit
ip route 192.168.2.0 255.255.255.0 10.0.0.2
end

R2
conf t
interface f0/0
 ip address 192.168.2.1 255.255.255.0
 no shutdown
interface f0/1
 ip address 10.0.0.2 255.255.255.252
 no shutdown
exit
ip route 192.168.1.0 255.255.255.0 10.0.0.1
end
```
Capture the WAN link with filter `icmp`, then `ping 192.168.2.2` from PC1. This is the readable "before" screenshot.

### IPSec config
```
R1
conf t
crypto isakmp policy 10
 encr aes
 hash sha256
 authentication pre-share
 group 2
 lifetime 86400
exit
crypto isakmp key VPN123 address 10.0.0.2
crypto ipsec transform-set MYSET esp-aes esp-sha-hmac
 mode tunnel
exit
ip access-list extended VPN-TRAFFIC
 permit ip 192.168.1.0 0.0.0.255 192.168.2.0 0.0.0.255
exit
crypto map VPN-MAP 10 ipsec-isakmp
 set peer 10.0.0.2
 set transform-set MYSET
 match address VPN-TRAFFIC
exit
interface f0/1
 crypto map VPN-MAP
end

R2: same, but
 crypto isakmp key VPN123 address 10.0.0.1
 permit ip 192.168.2.0 0.0.0.255 192.168.1.0 0.0.0.255
 set peer 10.0.0.1
```
Make sure both routers have `hash sha256` (a missing hash line on one side stops the tunnel) and that the ACLs are mirror images.

### Verify
```
R1# ping 192.168.2.2 source f0/0
show crypto isakmp sa        QM_IDLE, ACTIVE = Phase 1 up
show crypto ipsec sa         encaps and decaps counting up, two SPIs
show crypto map
```
Wireshark: filter `esp` or `isakmp || esp`. Before the VPN: ICMP, 192.168.1.2 to 192.168.2.2, 98 bytes. After: ESP, only 10.0.0.1 and 10.0.0.2, 166 bytes, two SPIs (one per direction).

### If it fails
`clear crypto isakmp` and `clear crypto sa`, then ping again. `debug crypto isakmp` shows why. A `QM_IDLE` with zero encaps means the crypto ACL does not match the traffic.

## Lab 3: GRE over IPsec, AES then RSA

Topology: PC1 (192.168.1.10) - R1 f0/0 192.168.1.1, R1 s1/0 10.0.0.1/24, Tunnel0 172.16.1.1 - R2 s1/0 10.0.0.2/24, Tunnel0 172.16.1.2, R2 f0/0 192.168.2.1 - PC2 (192.168.2.10).

### Base config
```
PC1> ip 192.168.1.10/24 192.168.1.1
PC2> ip 192.168.2.10/24 192.168.2.1

R1
conf t
hostname R1
ip domain-name lab.local
interface f0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface s1/0
 ip address 10.0.0.1 255.255.255.0
 no shutdown
exit
ip route 192.168.2.0 255.255.255.0 10.0.0.2
end

R2
conf t
hostname R2
ip domain-name lab.local
interface f0/0
 ip address 192.168.2.1 255.255.255.0
 no shutdown
interface s1/0
 ip address 10.0.0.2 255.255.255.0
 no shutdown
exit
ip route 192.168.1.0 255.255.255.0 10.0.0.1
end
```
If Serial1/0 is up/down, add `clock rate 64000` under the interface on one end. Capture the serial link with `icmp` and ping for the readable "before" screenshot.

### GRE tunnel
```
R1
conf t
interface Tunnel0
 ip address 172.16.1.1 255.255.255.0
 tunnel source s1/0
 tunnel destination 10.0.0.2
exit
ip route 192.168.2.0 255.255.255.0 172.16.1.2
no ip route 192.168.2.0 255.255.255.0 10.0.0.2
end

R2
conf t
interface Tunnel0
 ip address 172.16.1.2 255.255.255.0
 tunnel source s1/0
 tunnel destination 10.0.0.1
exit
ip route 192.168.1.0 255.255.255.0 172.16.1.1
no ip route 192.168.1.0 255.255.255.0 10.0.0.1
end
```
The handout keeps the old direct route next to the tunnel route. Removing it forces the traffic through the tunnel. Ping again, and filter `gre` to see ICMP inside GRE.

### IPsec with AES (symmetric)
```
R1
conf t
crypto isakmp policy 10
 encr aes 256
 hash sha
 authentication pre-share
 group 2
 lifetime 86400
exit
crypto isakmp key cisco123 address 10.0.0.2
crypto ipsec transform-set MYSET esp-aes 256 esp-sha-hmac
 mode tunnel
exit
access-list 100 permit gre host 10.0.0.1 host 10.0.0.2
crypto map MYMAP 10 ipsec-isakmp
 set peer 10.0.0.2
 set transform-set MYSET
 match address 100
exit
interface s1/0
 crypto map MYMAP
end

R2: same, but
 crypto isakmp key cisco123 address 10.0.0.1
 access-list 100 permit gre host 10.0.0.2 host 10.0.0.1
 set peer 10.0.0.1
```
Verify with `show crypto isakmp sa` (QM_IDLE) and `show crypto ipsec sa`. Wireshark: `esp` (the GRE and ICMP are now unreadable) and `udp.port == 500` (IKE negotiation).

### RSA (asymmetric) policy
```
R1 and R2
conf t
crypto key generate rsa modulus 1024
crypto isakmp policy 20
 encr aes
 hash sha
 authentication rsa-sig
 group 2
 lifetime 86400
end
show crypto key mypubkey rsa
```
The handout stops here. `rsa-sig` negotiation also needs certificates from a CA, which the handout does not set up, so the tunnel keeps using the pre-shared key policy 10. Say this if asked. Mapping for the write-up: IKE (UDP 500) is where asymmetric crypto (RSA and Diffie-Hellman) happens, ESP is where symmetric crypto (AES) protects the data.

## Lab 6: OSPF with plain-text then MD5 authentication

Topology: PC1 (192.168.1.2) - R1 f0/0 192.168.1.1, R1 g1/0 192.168.2.1 - R2 g1/0 192.168.2.2, R2 g2/0 192.168.3.1 - R3 g2/0 192.168.3.2, R3 f0/0 192.168.4.1 - PC2 (192.168.4.2).

Handout traps: the IP table is wrong, use the configuration steps below. The test ping is `192.168.4.2`, not `192.168.3.10`. The auth commands go under the interface, not at `(config-router)#`.

### Addressing
```
PC1> ip 192.168.1.2/24 192.168.1.1
PC2> ip 192.168.4.2/24 192.168.4.1

R1
conf t
hostname R1
interface f0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface g1/0
 ip address 192.168.2.1 255.255.255.0
 no shutdown
end

R2
conf t
hostname R2
interface g1/0
 ip address 192.168.2.2 255.255.255.0
 no shutdown
interface g2/0
 ip address 192.168.3.1 255.255.255.0
 no shutdown
end

R3
conf t
hostname R3
interface g2/0
 ip address 192.168.3.2 255.255.255.0
 no shutdown
interface f0/0
 ip address 192.168.4.1 255.255.255.0
 no shutdown
end
```

### OSPF
```
R1: router ospf 1 / network 192.168.1.0 0.0.0.255 area 0 / network 192.168.2.0 0.0.0.255 area 0
R2: router ospf 1 / network 192.168.2.0 0.0.0.255 area 0 / network 192.168.3.0 0.0.0.255 area 0
R3: router ospf 1 / network 192.168.3.0 0.0.0.255 area 0 / network 192.168.4.0 0.0.0.255 area 0
```
Wait about 40 seconds, then `show ip ospf neighbor` on each router (want FULL) and `ping 192.168.4.2` from PC1.

### Plain-text authentication
Start the capture on the R1 to R2 link with filter `ospf` first. Then on R1 g1/0, R2 g1/0, R2 g2/0 and R3 g2/0:
```
conf t
interface g1/0              (g2/0 where that is the link)
 ip ospf authentication
 ip ospf authentication-key 12345
end
```
Wireshark Hello: `Auth Type: Simple password (1)` and `Auth Data (Simple): 12345`. The password is readable.

### MD5 authentication
Same four interfaces, both ends of a link close together:
```
conf t
interface g1/0              (g2/0 where that is the link)
 ip ospf message-digest-key 1 md5 MySecretKey
 ip ospf authentication message-digest
end
```
Verify:
```
show ip ospf neighbor            FULL
show ip ospf interface g1/0      "Message digest authentication enabled", "Youngest key id is 1"
ping 192.168.4.2                 from PC1
```
Wireshark Hello (a new one): `Auth Type: Cryptographic (2)`, Key id 1, data length 16, a crypto sequence number and a 16 byte digest. The key is not in the packet.

If a neighbour stays down: the key or key ID differs, or one side is missing `ip ospf authentication`. Fix it, then `clear ip ospf process` and answer `yes`.

## Why questions

- **Plain-text vs MD5:** plain-text sends the password in every packet. MD5 sends a key ID, a sequence number and a keyed digest, so the receiver can check the packet is unchanged and from a router that knows the key, without seeing the key. The sequence number stops replays. It is not encryption, the routes are still readable.
- **IPsec Phase 1 vs Phase 2:** Phase 1 builds a secure channel between the routers (authentication, Diffie-Hellman key exchange, IKE on UDP 500). Phase 2 builds the IPsec SAs that protect the data with ESP, one SA per direction.
- **Tunnel mode ESP:** the whole original packet, including its IP header, is encrypted and wrapped in a new outer IP header. The WAN shows only the two router addresses.
- **Symmetric vs asymmetric:** asymmetric (RSA, DH) is slow and used for authentication and key exchange. Symmetric (AES) is fast and protects the actual data.
- **Crypto ACL:** defines which traffic gets encrypted. It must mirror on both routers.
- **Weak points to mention:** static pre-shared keys, DH group 2 is dated, no PFS, only the interesting traffic is protected, MD5 is an old hash, encryption still leaks addresses, sizes and timing.
