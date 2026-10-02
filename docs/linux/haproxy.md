# HAProxy Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for HAProxy service checks, configuration validation, statistics, and runtime administration. Runtime commands and socket paths depend on the HAProxy release and local configuration.

## Safety

Inspect configuration, backend health, and current sessions before runtime changes. Disabling a backend, terminating sessions, or clearing stick-tables can affect live traffic. Capture counters and table contents before removing evidence.

## Quick reference

### Service Status and Configuration

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `sudo systemctl status haproxy` | Checks the current status of the HAProxy service. |
| — | `sudo haproxy -c -V -f /etc/haproxy/haproxy.cfg` | Validates the HAProxy configuration file for syntax errors. |
| — | `sudo haproxy -vv` | Displays HAProxy version and build options. |

### Monitoring and Statistics

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `echo "show info" \| sudo socat stdio /var/run/haproxy.sock` | Displays general information about the running HAProxy instance. |
| — | `echo "show stat" \| sudo socat stdio /var/run/haproxy.sock` | Shows statistics for all servers and frontends. |
| — | `echo "show errors" \| sudo socat stdio /var/run/haproxy.sock` | Displays recent HTTP errors and their details. |
| — | `tail -f /var/log/haproxy.log` | Continuously monitors the HAProxy log file. |
| — | `echo "show rate" \| sudo socat stdio /var/run/haproxy.sock` | Displays the current session rate. |

### Session and Backend Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `echo "show sess" \| sudo socat stdio /var/run/haproxy.sock` | Lists currently active sessions. |
| — | `echo "show backend" \| sudo socat stdio /var/run/haproxy.sock` | Lists available backends and their status. |
| `echo "show stat" \| sudo socat stdio /var/run/haproxy.sock` | `echo "disable server <backend>/<server>" \| sudo socat stdio /var/run/haproxy.sock` | Temporarily disables a server in a backend. **Caution:** Changes live traffic placement. |
| `echo "show stat" \| sudo socat stdio /var/run/haproxy.sock` | `echo "enable server <backend>/<server>" \| sudo socat stdio /var/run/haproxy.sock` | Re-enables a previously disabled server. **Caution:** Returns a server to traffic handling. |
| `echo "show stat" \| sudo socat stdio /var/run/haproxy.sock` | `echo "set weight <backend>/<server> <weight>" \| sudo socat stdio /var/run/haproxy.sock` | Changes the weight of a server in load balancing. **Caution:** Changes live traffic distribution. |
| — | `echo "get weight <backend>/<server>" \| sudo socat stdio /var/run/haproxy.sock` | Displays the current weight of a server. |
| `echo "show stat" \| sudo socat stdio /var/run/haproxy.sock` | `echo "shutdown session <session-id>" \| sudo socat stdio /var/run/haproxy.sock` | Forcefully terminates a session. **Caution:** Disruptive: terminates an active session; inspect `show sess` first. |

### Management and Debugging

| Inspect first | Command | Effect / caution |
|---|---|---|
| `echo "show stat" \| sudo socat stdio /var/run/haproxy.sock` | `echo "clear counters" \| sudo socat stdio /var/run/haproxy.sock` | Clears all counters in the proxy (does not reset current sessions). **Caution:** Removes diagnostic evidence; capture `show stat` first. |
| — | `echo "show table" \| sudo socat stdio /var/run/haproxy.sock` | Displays stick-tables and their contents. |
| `echo "show stat" \| sudo socat stdio /var/run/haproxy.sock` | `echo "clear table <table>" \| sudo socat stdio /var/run/haproxy.sock` | Clears a specific stick-table. **Caution:** Destructive: removes stick-table entries; inspect `show table` first. |
| — | `echo "show health" \| sudo socat stdio /var/run/haproxy.sock` | Displays health check details. |
| — | `echo "show map <map>" \| sudo socat stdio /var/run/haproxy.sock` | Displays the content of a map file. |
| `echo "show stat" \| sudo socat stdio /var/run/haproxy.sock` | `echo "add map <map> <key> <value>" \| sudo socat stdio /var/run/haproxy.sock` | Adds an entry to a map file. **Caution:** Changes live mapping behavior; inspect the map first. |
| `echo "show stat" \| sudo socat stdio /var/run/haproxy.sock` | `echo "del map <map> <key>" \| sudo socat stdio /var/run/haproxy.sock` | Deletes an entry from a map file. **Caution:** Destructive: removes a live mapping; inspect the map first. |
| — | `echo "show resolvers" \| sudo socat stdio /var/run/haproxy.sock` | Displays details of DNS resolvers. |
| — | `echo "show tls-keys" \| sudo socat stdio /var/run/haproxy.sock` | Lists TLS keys. |
| — | `echo "show threads" \| sudo socat stdio /var/run/haproxy.sock` | Displays information about HAProxy threads. |
| — | `echo "show pools" \| sudo socat stdio /var/run/haproxy.sock` | Shows memory pool usage. |
| — | `echo "show fd" \| sudo socat stdio /var/run/haproxy.sock` | Displays file descriptor usage. |
| — | `echo "show runtime errors" \| sudo socat stdio /var/run/haproxy.sock` | Lists runtime errors since last boot. |

## Troubleshooting workflow

1. Confirm the affected frontend, backend, server, and failure time.
2. Inspect service status, configuration validity, and runtime statistics without changing traffic handling.
3. Capture logs, error details, health-check results, and counters before clearing evidence.
4. Compare the active configuration, endpoints, certificates, and weights with the intended state.
5. Apply a targeted, reviewed correction and preserve the previous configuration.
6. Verify backend health and a client request; record runtime changes and rollback settings.

## Official references

- [HAProxy documentation](https://www.haproxy.org/#docs)
