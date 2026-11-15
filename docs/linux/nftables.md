# nftables Cheat Sheet

> **Applies to:** Linux systems using nftables 1.0 or later with the `nft` command
> **Last reviewed:** 2026-11-14

nftables is the packet-classification framework that replaced iptables, ip6tables, arptables, and ebtables in the Linux kernel. Debian, Ubuntu, and the RHEL family use it as the default firewall backend, often behind firewalld, UFW, or the `iptables-nft` compatibility layer. See [iptables](iptables.md) for hosts still managed through the older command.

## Safety

> [!WARNING]
> A wrong ruleset can cut off SSH. Keep console or out-of-band access, save the current ruleset before changing it, and prefer an atomic file load with a timed rollback over editing live rules one at a time.

- `nft flush ruleset` removes every table, including ones owned by Docker, Kubernetes, libvirt, firewalld, or fail2ban. Flush or delete only your own table.
- Do not mix native `nft` rules with `iptables-nft`, firewalld, or UFW management of the same hooks without understanding hook priority; every base chain on a hook is evaluated, and a `drop` in any one of them is final.
- An `accept` verdict ends evaluation only in the current base chain. A later-priority chain on the same hook can still drop the packet.
- Rule handles and positions change when rules are added or removed. Read the handle immediately before deleting by handle.

Save the current state first:

```bash
sudo nft list ruleset > /root/nftables-$(date +%Y%m%d-%H%M%S).nft
```

## Quick reference

### Concepts

| Term | Meaning |
|---|---|
| Family | Packet type a table handles: `ip`, `ip6`, `inet` (both), `arp`, `bridge`, `netdev` |
| Table | Namespace for chains, sets, and maps; has no built-in behavior |
| Base chain | Chain attached to a kernel hook with a type, hook, and priority |
| Regular chain | Chain reached only through `jump` or `goto` |
| Hook | `prerouting`, `input`, `forward`, `output`, `postrouting`, and `ingress` |
| Priority | Order of base chains on one hook; lower runs first (`filter` is 0, `dstnat` is -100, `srcnat` is 100) |
| Policy | Verdict for packets that reach the end of a base chain: `accept` or `drop` |
| Set | Collection of addresses, ports, or other values matched in one lookup |
| Verdict map | Map from a key to a verdict, such as an interface name to a chain |
| Handle | Kernel-assigned identifier of a rule, chain, or set, shown with `-a` |

Nothing exists by default. There are no predefined `filter`, `nat`, or `INPUT` objects unless a distribution file or another tool creates them.

### Find out what manages the firewall

```bash
sudo nft list tables
systemctl is-active nftables firewalld ufw
iptables --version
```

`iptables --version` prints `nf_tables` or `legacy` to show which backend the compatibility command uses. Tables named `ip filter` and `ip nat` with uppercase chains usually come from `iptables-nft`; a table named `inet firewalld` belongs to firewalld.

### Inspect

```bash
sudo nft list ruleset
sudo nft -a list ruleset
sudo nft list table inet <table>
sudo nft -a list chain inet <table> <chain>
sudo nft list sets
sudo nft list set inet <table> <set>
sudo nft list counters
```

Use `-a` to show handles, `-n` to skip name resolution, and `-j` for JSON output.

### Minimal host firewall

A typical `/etc/nftables.conf` for a server. The leading `table` and `delete table` pair makes the file safe to reload without touching other tables.

```nft
#!/usr/sbin/nft -f

table inet host_filter
delete table inet host_filter

table inet host_filter {
    set admin_v4 {
        type ipv4_addr
        flags interval
        elements = { <admin-cidr> }
    }

    chain input {
        type filter hook input priority filter; policy drop;

        ct state established,related accept
        ct state invalid drop
        iif "lo" accept

        meta l4proto { icmp, ipv6-icmp } accept
        ip saddr @admin_v4 tcp dport 22 accept
        tcp dport { 80, 443 } accept

        counter comment "dropped by policy"
    }

    chain forward {
        type filter hook forward priority filter; policy drop;
    }

    chain output {
        type filter hook output priority filter; policy accept;
    }
}
```

ICMPv6 must stay reachable for neighbor discovery and path MTU discovery; tighten it by type only when the required types are understood.

### Validate and load atomically

```bash
sudo nft -c -f /etc/nftables.conf
sudo nft -f /etc/nftables.conf
```

`-c` parses and checks without applying. A file load is one transaction: either every statement applies or none does.

Load with a timed rollback when working over SSH. If the new rules lock the session out, the saved ruleset returns after two minutes:

```bash
{ echo "flush ruleset"; sudo nft list ruleset; } | sudo tee /root/nft-rollback.nft > /dev/null
sudo systemd-run --on-active=2min --unit=nft-rollback nft -f /root/nft-rollback.nft
sudo nft -f /etc/nftables.conf
```

Open a second SSH session to confirm access, then cancel the rollback:

```bash
sudo systemctl stop nft-rollback.timer
```

The rollback file starts with `flush ruleset`, which is acceptable only because the complete saved state is restored in the same atomic transaction.

### Change live rules

```bash
sudo nft add rule inet <table> input tcp dport 8443 accept
sudo nft insert rule inet <table> input position <handle> ip saddr <source-cidr> drop
sudo nft replace rule inet <table> input handle <handle> tcp dport 8443 counter accept
sudo nft -a list chain inet <table> input
sudo nft delete rule inet <table> input handle <handle>
```

`add` appends, and `insert` places a rule at the start or before the given handle. Live changes are lost at the next reload or reboot unless they are also written to the configuration file.

### Sets and maps

```bash
sudo nft add element inet <table> <set> { <cidr-1>, <cidr-2> }
sudo nft delete element inet <table> <set> { <cidr-1> }
sudo nft flush set inet <table> <set>
```

Updating a set changes matching for every rule that references it without rewriting the rules. A dynamic set can rate-limit per source:

```nft
set ssh_meter {
    type ipv4_addr
    flags dynamic
    timeout 1m
}

chain input {
    tcp dport 22 ct state new add @ssh_meter { ip saddr limit rate 10/minute } accept
}
```

A verdict map dispatches by key in one lookup:

```nft
iifname vmap { "eth0" : jump from_wan, "eth1" : jump from_lan }
```

### NAT

```nft
table ip nat {
    chain prerouting {
        type nat hook prerouting priority dstnat;
        iifname "<wan-interface>" tcp dport 443 dnat to <internal-ip>:8443
    }

    chain postrouting {
        type nat hook postrouting priority srcnat;
        oifname "<wan-interface>" masquerade
    }
}
```

Forwarded traffic also needs `net.ipv4.ip_forward=1` and an `accept` in the `forward` chain. Only the first packet of a connection traverses NAT chains; inspect translations with `conntrack -L`.

### Logging, counters, and tracing

```bash
sudo nft add rule inet <table> input tcp dport 23 log prefix \"telnet-drop \" counter drop
sudo nft list chain inet <table> input
sudo nft reset counters inet <table>
```

Trace how a specific flow is evaluated without logging everything:

```bash
sudo nft add chain inet <table> trace_pre '{ type filter hook prerouting priority -350; }'
sudo nft add rule inet <table> trace_pre ip saddr <source-ip> tcp dport <port> meta nftrace set 1
sudo nft monitor trace
sudo nft delete chain inet <table> trace_pre
```

`nft monitor trace` prints each chain, rule, and verdict the packet meets, across every table. Remove the trace chain when finished.

### Persistence

| Distribution | Configuration file | Enable at boot |
|---|---|---|
| Debian, Ubuntu | `/etc/nftables.conf` | `systemctl enable --now nftables` |
| RHEL, Fedora, AlmaLinux, Rocky | `/etc/sysconfig/nftables.conf` | `systemctl enable --now nftables` (disable firewalld first if using native rules) |

`systemctl reload nftables` re-reads the file. `systemctl stop nftables` flushes the ruleset on Debian-family packages.

### Translate from iptables

```bash
iptables-translate -A INPUT -p tcp --dport 22 -s <source-cidr> -j ACCEPT
iptables-save > rules.v4
iptables-restore-translate -f rules.v4 > ruleset.nft
```

Review translated output before loading it. Extensions without a native equivalent are emitted as comments, and the result keeps iptables-style table and chain names.

### Containers and Kubernetes

- Docker Engine programs its own tables; current releases can use a native nftables backend instead of iptables. Publish-port rules bypass a host `input` chain because the traffic is forwarded, so restrict it in `forward` or in Docker's user chain.
- kube-proxy has an `nftables` mode that is generally available in current Kubernetes releases, alongside `iptables` and `ipvs`. Do not edit tables owned by kube-proxy or a CNI plugin.
- On container hosts, never flush the whole ruleset; restart the owning service if its tables are lost.

### Common failure patterns

| Symptom | Checks |
|---|---|
| Rule is present but traffic is still dropped | Another base chain on the same hook, chain policy, rule order, `ct state invalid` |
| Rules vanish after reboot | `nftables.service` not enabled, changes made live but not written to the file |
| Rules vanish at random | firewalld, UFW, Docker, or a config-management run reloading its own ruleset |
| `iptables -L` shows nothing but traffic is filtered | Rules live in native nftables tables that the iptables view does not show |
| Port forward works from outside but not from the host | Locally generated traffic uses `output`, not `prerouting` |
| Load fails with `File exists` or `No such file or directory` | Object already defined, or a referenced set, chain, or interface is missing at load time |
| IPv6 breaks after enabling a drop policy | ICMPv6 neighbor discovery not accepted |

## Troubleshooting workflow

1. Confirm the affected flow: source, destination, protocol, port, direction, and interface.
2. Identify who owns the firewall with `nft list tables` and the service checks; do not assume the configuration file reflects the running state.
3. Save the ruleset, then read every base chain on the relevant hook in priority order with `nft -a list ruleset`.
4. Check rule counters, connection tracking (`conntrack -L`), and routing (`ip route get <destination>`) before changing rules.
5. Trace the flow with `meta nftrace set 1` and `nft monitor trace` to find the exact rule and verdict.
6. Validate the corrected file with `nft -c -f`, load it atomically with a timed rollback, and confirm access from a second session.
7. Persist the change in the configuration file or the owning tool, remove trace and temporary rules, and record the previous ruleset location.

## Official references

- [nftables wiki](https://wiki.nftables.org/)
- [nft manual page](https://www.netfilter.org/projects/nftables/manpage.html)
- [Netfilter documentation](https://www.netfilter.org/documentation/)
