# HAProxy Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for HAProxy service checks, configuration validation, statistics, and runtime administration. Runtime commands and socket paths depend on the HAProxy release and local configuration.

## Safety

Inspect configuration, backend health, and current sessions before runtime changes. Disabling a backend, terminating sessions, or clearing stick-tables can affect live traffic. Capture counters and table contents before removing evidence.

## Quick reference

### Runtime API access

The examples use `/run/haproxy/admin.sock`, the Debian and Ubuntu package default. Check the `stats socket` line in the `global` section for the real path and make sure it is declared with `level admin` before using commands that change state. Set it once:

```bash
SOCK=/run/haproxy/admin.sock
echo "help" | sudo socat stdio "$SOCK"
```

`help` lists the commands the running release supports; the set differs between major versions.

### Service status and configuration

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `sudo systemctl status haproxy` | Shows service state. |
| — | `sudo haproxy -c -f /etc/haproxy/haproxy.cfg` | Validates the configuration file. |
| — | `haproxy -vv` | Shows version, build options, and compiled-in features. |
| `sudo haproxy -c -f /etc/haproxy/haproxy.cfg` | `sudo systemctl reload haproxy` | Loads new configuration with a seamless reload. **Caution:** Runtime API changes not written to the file are lost. |
| — | `journalctl -u haproxy -f` | Follows logs (or the file your syslog rule writes, commonly `/var/log/haproxy.log`). |

### Monitoring and statistics

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `echo "show info" \| sudo socat stdio "$SOCK"` | Process-wide information: uptime, connections, rates, limits. |
| — | `echo "show stat" \| sudo socat stdio "$SOCK"` | CSV statistics for every frontend, backend, and server. |
| — | `echo "show servers state <backend>" \| sudo socat stdio "$SOCK"` | Operational and administrative state of each server. |
| — | `echo "show backend" \| sudo socat stdio "$SOCK"` | Lists backend names. |
| — | `echo "show errors" \| sudo socat stdio "$SOCK"` | Last captured invalid request or response per proxy. |
| — | `echo "show sess" \| sudo socat stdio "$SOCK"` | Lists active streams. |
| — | `echo "show table" \| sudo socat stdio "$SOCK"` | Lists stick-tables; add a table name to dump entries. |
| — | `echo "show resolvers" \| sudo socat stdio "$SOCK"` | DNS resolver statistics. |
| — | `echo "show ssl cert" \| sudo socat stdio "$SOCK"` | Lists loaded certificates; add a filename for details and expiry. |

### Server and traffic changes

| Inspect first | Command | Effect / caution |
|---|---|---|
| `show servers state <backend>` | `echo "set server <backend>/<server> state drain" \| sudo socat stdio "$SOCK"` | Stops new connections while existing ones finish. **Caution:** Shifts traffic to the remaining servers. |
| `show servers state <backend>` | `echo "set server <backend>/<server> state maint" \| sudo socat stdio "$SOCK"` | Takes a server out of rotation (same as `disable server`). **Caution:** Disruptive for that server's sessions. |
| `show servers state <backend>` | `echo "set server <backend>/<server> state ready" \| sudo socat stdio "$SOCK"` | Returns a server to rotation (same as `enable server`). |
| `echo "get weight <backend>/<server>"` | `echo "set weight <backend>/<server> <weight>" \| sudo socat stdio "$SOCK"` | Changes a server's weight. **Caution:** Changes live traffic distribution. |
| `show sess` | `echo "shutdown session <session-id>" \| sudo socat stdio "$SOCK"` | Terminates one stream. **Caution:** Disruptive for that client. |
| `show sess` | `echo "shutdown sessions server <backend>/<server>" \| sudo socat stdio "$SOCK"` | Terminates every stream on a server. **Caution:** Disruptive. |

### Maps, tables, and counters

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `echo "show map" \| sudo socat stdio "$SOCK"` | Lists maps with their IDs; add `#<id>` or a path to dump entries. |
| `show map <map>` | `echo "add map <map> <key> <value>" \| sudo socat stdio "$SOCK"` | Adds a map entry. **Caution:** Changes live routing decisions and is not written to the file. |
| `show map <map>` | `echo "del map <map> <key>" \| sudo socat stdio "$SOCK"` | Removes a map entry. **Caution:** Destructive for that mapping. |
| `show table <table>` | `echo "clear table <table> key <key>" \| sudo socat stdio "$SOCK"` | Removes one stick-table entry. **Caution:** Without `key` or a filter it clears the whole table. |
| `show stat` | `echo "clear counters" \| sudo socat stdio "$SOCK"` | Resets max counters (`clear counters all` resets everything). **Caution:** Removes diagnostic evidence; save `show stat` first. |

### Process diagnostics

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `echo "show threads" \| sudo socat stdio "$SOCK"` | Per-thread state, useful for stuck-thread reports. |
| — | `echo "show pools" \| sudo socat stdio "$SOCK"` | Memory pool usage. |
| — | `echo "show fd" \| sudo socat stdio "$SOCK"` | Open file descriptors and their owners. |
| — | `echo "show activity" \| sudo socat stdio "$SOCK"` | Per-thread scheduler and polling counters. |

## Troubleshooting workflow

1. Confirm the affected frontend, backend, server, and failure time.
2. Inspect service status, configuration validity, and runtime statistics without changing traffic handling.
3. Capture logs, error details, health-check results, and counters before clearing evidence.
4. Compare the active configuration, endpoints, certificates, and weights with the intended state.
5. Apply a targeted, reviewed correction and preserve the previous configuration.
6. Verify backend health and a client request; record runtime changes and rollback settings.

## Official references

- [HAProxy documentation](https://www.haproxy.org/#docs)
- [HAProxy Management Guide](https://docs.haproxy.org/)
