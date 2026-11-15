# Debian Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for Debian package inspection, services, logs, processes, files, and remote access. Confirm package-manager and service behavior against the installed Debian release.

## Safety

Inspect package, service, process, and filesystem state before changing it. Package removal, purge, service stops, process termination, and permission changes can interrupt workloads. Preserve relevant configuration and review the affected packages before proceeding.

## Quick reference

### Release notes

Debian 13 (trixie) is the current stable release and Debian 12 (bookworm) is oldstable. Recent releases ship APT 3 and prefer deb822 source files in `/etc/apt/sources.list.d/*.sources`; `apt modernize-sources` converts the older one-line format. `apt` is the interactive front end; use `apt-get` and `apt-cache` in scripts because their output is stable.

### Package inspection

| Command | Purpose |
|---|---|
| `cat /etc/os-release` | Release name and version (`lsb_release -a` needs the `lsb-release` package). |
| `apt list --upgradable` | Packages with a newer candidate after `apt update`. |
| `apt policy <package>` | Installed version, candidate, and which repository supplies it. |
| `apt show <package>` | Package description and dependencies. |
| `apt search <keyword>` | Searches package names and descriptions. |
| `apt-mark showhold` | Packages held back from upgrades. |
| `dpkg -l '<pattern>'` | Installed packages matching a pattern. |
| `dpkg -s <package>` | Status and version of one installed package. |
| `dpkg -L <package>` | Files installed by a package. |
| `dpkg -S <file-path>` | Package that owns a file. |
| `less /var/log/apt/history.log` | What APT installed, upgraded, or removed, and when. |

### Package changes

Add `-s` (simulate) to any `apt` or `apt-get` change to see the full transaction first.

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `sudo apt update` | Refreshes package indexes. Changes no installed packages. |
| `apt list --upgradable` | `sudo apt upgrade` | Upgrades packages without removing any. **Caution:** Can restart services. |
| `apt -s full-upgrade` | `sudo apt full-upgrade` | Upgrades and allows removals to resolve dependencies (same as `apt-get dist-upgrade`). **Caution:** Review removals; this is the command for a release upgrade after sources are changed, not a release upgrade by itself. |
| `apt policy <package>` | `sudo apt install <package>` | Installs or upgrades one package. **Caution:** Pulls in dependencies. |
| `apt -s remove <package>` | `sudo apt remove <package>` | Removes a package and keeps its configuration. **Caution:** Can remove packages that depend on it. |
| `apt -s purge <package>` | `sudo apt purge <package>` | Removes a package and its configuration files. **Caution:** Destructive for system-wide configuration. |
| `apt -s autoremove` | `sudo apt autoremove` | Removes automatically installed packages nothing depends on. **Caution:** Review the list; old kernels are included. |
| `apt policy <package>` | `sudo apt-mark hold <package>` | Pins a package at its current version (`unhold` reverses it). **Caution:** Also blocks security updates for it. |
| `dpkg -I <package-file.deb>` | `sudo apt install ./<package-file.deb>` | Installs a local package and resolves dependencies, unlike `dpkg -i`. **Caution:** Verify the source of the file. |
| `dpkg --audit` | `sudo dpkg --configure -a` | Finishes an interrupted installation. **Caution:** Runs pending maintainer scripts. |

### Services and logs

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `systemctl status <service>` | State, recent log lines, and main PID. |
| — | `systemctl --failed` | Units in a failed state. |
| — | `journalctl -u <service> --since "<time>"` | Logs for one unit from a point in time. |
| — | `journalctl -fu <service>` | Follows a unit's logs. |
| — | `journalctl -p err -b` | Errors since the current boot. |
| `systemctl status <service>` | `sudo systemctl restart <service>` | Restarts a service. **Caution:** Disruptive; prefer `reload` when the service supports it. |
| `systemctl status <service>` | `sudo systemctl stop <service>` | Stops a service. **Caution:** Disruptive. |
| `systemctl is-enabled <service>` | `sudo systemctl enable --now <service>` | Enables at boot and starts now. **Caution:** Changes startup behavior. |
| `systemctl is-enabled <service>` | `sudo systemctl disable --now <service>` | Disables at boot and stops now. **Caution:** Disruptive. |
| — | `needrestart` | Lists services still running old libraries after an upgrade, if the package is installed. |

### System state

| Command | Purpose |
|---|---|
| `uname -r` | Running kernel version. |
| `hostnamectl` | Hostname, machine ID, and virtualization. |
| `df -hT` | Filesystem usage and type. |
| `du -xsh <directory>` | Size of a directory on one filesystem. |
| `free -h` | Memory and swap. |
| `ps aux --sort=-%mem` | Processes, largest memory users first. |
| `ss -tulpn` | Listening sockets and owning processes. |
| `ip -br address` | Interface addresses in brief form. |
| `[ -f /var/run/reboot-required ] && cat /var/run/reboot-required.pkgs` | Whether an upgrade is waiting on a reboot. |

### Processes and scheduled jobs

| Inspect first | Command | Effect / caution |
|---|---|---|
| `ps -fp <pid>` | `kill <pid>` | Sends SIGTERM. **Caution:** Disruptive; use `kill -9` only when a process ignores SIGTERM. |
| `pgrep -a <process-name>` | `pkill <process-name>` | Signals every matching process. **Caution:** Disruptive; check the match list first. |
| `crontab -l` | `crontab -e` | Edits the current user's cron jobs. **Caution:** Changes scheduled tasks. |
| — | `systemctl list-timers` | systemd timers, including APT's daily jobs. |

### Files and transfers

| Inspect first | Command | Effect / caution |
|---|---|---|
| `tar -tzf <archive.tar.gz>` | `tar -xzf <archive.tar.gz> -C <directory>` | Extracts an archive. **Caution:** Overwrites existing files of the same name. |
| `ls -l <file>` | `chmod <mode> <file>` | Changes permissions. **Caution:** `-R` on the wrong path is hard to undo. |
| `ls -l <file>` | `chown <user>:<group> <file>` | Changes ownership. **Caution:** Same as above. |
| `rsync -avzn <source> <user>@<host>:<destination>` | `rsync -avz <source> <user>@<host>:<destination>` | Copies changed files over SSH. **Caution:** `--delete` removes files at the destination; always dry-run it. |

See [iptables](iptables.md) and [nftables](nftables.md) for packet filtering, and [scp](scp.md) for file copy over SSH.

## Troubleshooting workflow

1. Confirm the host, Debian release, affected package or service, and failure time.
2. Inspect package status, service state, disk space, and processes before restarting or removing anything.
3. Collect relevant journal entries and package-manager logs with timestamps.
4. Compare installed versions, configuration, permissions, and recent changes with the intended state.
5. Apply the least disruptive package or configuration correction.
6. Verify service and client behavior, then record the change and previous configuration.

## Official references

- [Debian Reference](https://www.debian.org/doc/manuals/debian-reference/)
- [Debian release notes](https://www.debian.org/releases/stable/releasenotes)
