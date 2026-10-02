# Debian Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for Debian package inspection, services, logs, processes, files, and remote access. Confirm package-manager and service behavior against the installed Debian release.

## Safety

Inspect package, service, process, and filesystem state before changing it. Package removal, purge, service stops, process termination, and permission changes can interrupt workloads. Preserve relevant configuration and review the affected packages before proceeding.

## Quick reference

### Package Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| `dpkg -l` | `sudo apt update` | Updates the package index. **Caution:** Changes the local package index. |
| `dpkg -l` | `sudo apt upgrade` | Upgrades all upgradable packages. **Caution:** Changes installed packages and may restart services. |
| `dpkg -l` | `sudo apt full-upgrade` | Upgrades packages with auto-handling of dependencies. **Caution:** Can remove packages while resolving dependencies; review the proposed changes. |
| `dpkg -l` | `sudo apt install <package-name>` | Installs a package. **Caution:** Changes installed packages. |
| `dpkg -l` | `sudo apt remove <package-name>` | Removes a package without removing dependencies. **Caution:** Destructive: removes the selected package. |
| `dpkg -l` | `sudo apt purge <package-name>` | Removes a package along with its configuration files. **Caution:** Destructive: removes the package and its configuration. |
| `dpkg -l` | `sudo apt autoremove` | Automatically removes all unused packages. **Caution:** Destructive: removes packages classified as unused. |
| `dpkg -l` | `sudo apt-get dist-upgrade` | Upgrades the distribution to the latest release. **Caution:** May add or remove packages; review the proposed dependency changes. |
| — | `sudo apt-cache search <keyword>` | Searches the package database for a keyword. |
| — | `sudo apt-cache show <package-name>` | Shows package details. |

### dpkg (Debian Package Management)

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `dpkg -l` | Lists all installed packages. |
| `dpkg -l` | `dpkg -i <package-file.deb>` | Installs a .deb package file. **Caution:** Changes installed packages. |
| `dpkg -l` | `dpkg -r <package-name>` | Removes a .deb package. **Caution:** Destructive: removes an installed package. |
| `dpkg -l` | `dpkg -P <package-name>` | Purges a .deb package. **Caution:** Destructive: removes the package and configuration. |
| — | `dpkg -s <package-name>` | Shows package info and status. |
| — | `dpkg -L <package-name>` | Lists files installed by a package. |
| — | `dpkg -S <file-path>` | Finds the package that installed a file. |

### System Information and Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `uname -a` | Displays kernel and system information. |
| — | `lsb_release -a` | Shows distribution information. |
| — | `hostnamectl` | Shows or sets the system hostname. |

### Service Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `systemctl status <service-name>` | Checks the status of a service. |
| `dpkg -l` | `systemctl start <service-name>` | Starts a service. **Caution:** Changes service state; inspect `systemctl status <service-name>` first. |
| `dpkg -l` | `systemctl stop <service-name>` | Stops a service. **Caution:** Disruptive: stops the service; inspect `systemctl status <service-name>` first. |
| `dpkg -l` | `systemctl restart <service-name>` | Restarts a service. **Caution:** Disruptive: restarts the service; inspect `systemctl status <service-name>` first. |
| `dpkg -l` | `systemctl enable <service-name>` | Enables a service to start on boot. **Caution:** Changes startup behavior; inspect `systemctl status <service-name>` first. |
| `dpkg -l` | `systemctl disable <service-name>` | Disables a service from starting on boot. **Caution:** Disables startup; inspect `systemctl status <service-name>` first. |

### System Monitoring and Logs

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `journalctl -xe` | Views detailed system logs. |
| — | `journalctl -fu <service-name>` | Follows the logs for a specific service. |
| — | `top` | Displays real-time system resource usage. |
| — | `htop` | An interactive process viewer (if installed). |
| — | `df -h` | Shows disk space usage. |
| — | `du -sh <directory>` | Shows the size of a directory. |
| — | `free -m` | Displays memory usage in MB. |
| — | `ps aux` | Shows running processes. |

### Process and Job Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| `dpkg -l` | `kill <pid>` | Kills a process by its PID. **Caution:** Disruptive: signals a process; inspect `ps aux` first. |
| `dpkg -l` | `killall <process-name>` | Kills all processes with the given name. **Caution:** Disruptive: targets every process with this name; inspect `ps aux` first. |
| `dpkg -l` | `crontab -e` | Edits the current user's cron jobs. **Caution:** Changes scheduled tasks; inspect `crontab -l` first. |
| — | `crontab -l` | Lists the current user's cron jobs. |

### File and Directory Operations

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `find <directory> -name <filename>` | Searches for a file in a directory. |
| — | `grep <pattern> <file>` | Searches inside a file for a pattern. |
| — | `tar -czvf <archive.tar.gz> <directory>` | Creates a gzipped tar archive. |
| `dpkg -l` | `tar -xzvf <archive.tar.gz>` | Extracts a gzipped tar archive. **Caution:** Can overwrite files during extraction; inspect `tar -tzvf <archive.tar.gz>` first. |
| `dpkg -l` | `chmod <permissions> <file>` | Changes file permissions. **Caution:** Changes permissions; inspect `ls -l <file>` first. |
| `dpkg -l` | `chown <user>:<group> <file>` | Changes file owner and group. **Caution:** Changes ownership; inspect `ls -l <file>` first. |

### Networking and Remote Access

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `ssh <user>@<host>` | Connects to a remote host via SSH. |
| `dpkg -l` | `scp <source> <user>@<host>:<destination>` | Copies files over SSH. **Caution:** Can overwrite destination files; inspect the destination first. |
| `dpkg -l` | `rsync -avz <source> <user>@<host>:<destination>` | Syncs files/directories over SSH. **Caution:** Changes destination files; inspect a dry run first. |
| — | `wget <url>` | Downloads files from the internet. |
| — | `curl -O <url>` | Fetches a file from a URL. |
| — | `iptables -L` | Lists all firewall rules. |

## Troubleshooting workflow

1. Confirm the host, Debian release, affected package or service, and failure time.
2. Inspect package status, service state, disk space, and processes before restarting or removing anything.
3. Collect relevant journal entries and package-manager logs with timestamps.
4. Compare installed versions, configuration, permissions, and recent changes with the intended state.
5. Apply the least disruptive package or configuration correction.
6. Verify service and client behavior, then record the change and previous configuration.

## Official references

- [Debian Reference](https://www.debian.org/doc/manuals/debian-reference/)
