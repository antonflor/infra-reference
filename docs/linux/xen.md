# XenServer and XCP-ng xe Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for XenServer and XCP-ng host, pool, virtual machine (VM), network, and storage administration using `xe`. These examples target the XAPI management interface; a host running only the Xen hypervisor uses `xl` instead.

## Safety

Confirm the pool, host, and VM UUID before each operation. Shutdown, reboot, suspend, and storage changes affect guests. Check running tasks, guest state, and backup availability before changing a VM or pool.

## Quick reference

### Scope notes

`xe` is the XAPI command line shared by XenServer 8 and XCP-ng. A host running the upstream Xen hypervisor without XAPI is managed with `xl` instead. Most `xe` commands accept `--minimal` for script-friendly output and `params=<field>,<field>` to choose columns.

### Hosts and pool

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `xe pool-list` | Shows the pool, its coordinator, and default storage. |
| — | `xe host-list params=uuid,name-label,enabled` | Lists hosts and whether they accept VMs. |
| — | `xe task-list` | Lists running and recently finished tasks. |
| `xe vm-list resident-on=<host-uuid>` | `xe host-disable uuid=<host-uuid>` | Stops new VMs starting on a host. **Caution:** First step of host maintenance. |
| `xe host-list` | `xe host-evacuate uuid=<host-uuid>` | Live-migrates every VM off a host. **Caution:** Needs capacity and shared storage on other hosts. |
| `xe host-list` | `xe host-enable uuid=<host-uuid>` | Returns a host to service. |
| `xe pool-list` | `xe pool-param-set uuid=<pool-uuid> name-label=<new-name>` | Changes a pool parameter. **Caution:** Changes pool configuration. |

### Virtual machines

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `xe vm-list is-control-domain=false` | Lists guest VMs without dom0 entries. |
| — | `xe vm-param-list uuid=<vm-uuid>` | Shows every parameter of a VM. |
| `xe vm-list` | `xe vm-start uuid=<vm-uuid>` | Starts a VM. **Caution:** Changes VM state. |
| `xe vm-list` | `xe vm-shutdown uuid=<vm-uuid>` | Clean guest shutdown. **Caution:** Disruptive; `force=true` is a power-off and risks data loss. |
| `xe vm-list` | `xe vm-reboot uuid=<vm-uuid>` | Clean guest reboot. **Caution:** Disruptive. |
| `xe vm-list` | `xe vm-suspend uuid=<vm-uuid>` | Saves memory to disk and stops the VM. **Caution:** Disruptive; needs space on the suspend SR. |
| `xe vm-list` | `xe vm-resume uuid=<vm-uuid>` | Resumes a suspended VM. |
| `xe host-list` | `xe vm-migrate uuid=<vm-uuid> host-uuid=<host-uuid> live=true` | Live-migrates a VM inside the pool. **Caution:** Brief pause; check destination capacity. |
| `xe sr-list` | `xe vm-snapshot uuid=<vm-uuid> new-name-label=<snapshot-name>` | Takes a disk snapshot. **Caution:** Consumes storage and lengthens the VDI chain. |
| — | `xe snapshot-list snapshot-of=<vm-uuid>` | Lists a VM's snapshots. |
| `xe sr-list` | `xe vm-clone uuid=<vm-uuid> new-name-label=<new-name>` | Fast-clones a halted VM. **Caution:** Creates VM and disk objects. |
| `xe vm-list` | `xe vm-export uuid=<vm-uuid> filename=<file.xva>` | Exports a halted VM or snapshot. **Caution:** Check destination free space; large exports are slow. |
| `xe sr-list` | `xe vm-import filename=<file.xva> sr-uuid=<sr-uuid>` | Imports a VM. **Caution:** Creates VM and storage objects. |
| — | `xe template-list` | Lists templates. |

### Networking

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `xe network-list` | Lists networks and their bridges. |
| — | `xe pif-list host-uuid=<host-uuid>` | Physical interfaces, VLANs, and bonds on a host. |
| — | `xe vif-list vm-uuid=<vm-uuid>` | Virtual interfaces of a VM. |
| — | `xe bond-list` | NIC bonds and their members. |

### Storage

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `xe sr-list params=uuid,name-label,type,physical-utilisation,physical-size` | Storage repositories with usage. |
| — | `xe pbd-list sr-uuid=<sr-uuid>` | Whether each host has the SR attached. |
| — | `xe vdi-list sr-uuid=<sr-uuid>` | Virtual disks in an SR. |
| — | `xe vbd-list vm-uuid=<vm-uuid>` | Disk attachments of a VM. |
| `xe sr-list` | `xe sr-scan uuid=<sr-uuid>` | Rescans an SR for new or removed disks. |

### Logs and diagnostics

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `tail -f /var/log/xensource.log` | XAPI log on the host. |
| — | `tail -f /var/log/SMlog` | Storage manager log. |
| — | `xe message-list` | Pool alerts and messages. |
| — | `xl list` | Domains as the hypervisor sees them, run from dom0. |
| — | `xe-toolstack-restart` | Restarts XAPI without touching running guests. **Caution:** Interrupts management connections and running tasks. |

## Troubleshooting workflow

1. Confirm the pool, host, VM UUID, and affected task.
2. Inspect host, VM, network, and storage lists before changing guest state.
3. Collect task status and the release-specific host logs with timestamps.
4. Compare VM placement, virtual interfaces, disks, and available host resources with the intended configuration.
5. Apply one targeted correction using the documentation for the installed XenServer release.
6. Verify guest and workload recovery, then record the configuration and recovery point.

## Official references

- [XenServer documentation](https://docs.xenserver.com/)
- [XCP-ng documentation](https://docs.xcp-ng.org/)
- [XenServer xe command-line interface](https://docs.xenserver.com/en-us/xenserver/9/command-line-interface)
