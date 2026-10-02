# XenServer xe Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for XenServer host, pool, virtual machine (VM), network, and storage administration using `xe`. These examples target the XenServer management interface; a Debian host running the Xen hypervisor uses different tooling.

## Safety

Confirm the pool, host, and VM UUID before each operation. Shutdown, reboot, suspend, and storage changes affect guests. Check running tasks, guest state, and backup availability before changing a VM or pool.

## Quick reference

### Host and System Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `xe host-list` | Lists all hosts in a pool. |
| — | `xe vm-list` | Lists all virtual machines. |
| `xe vm-list` | `xe vm-start uuid=<vm-uuid>` | Starts a specific virtual machine. **Caution:** Changes VM state. |
| `xe vm-list` | `xe vm-shutdown uuid=<vm-uuid>` | Shuts down a specific virtual machine. **Caution:** Disruptive: stops the guest. |
| `xe vm-list` | `xe vm-reboot uuid=<vm-uuid>` | Reboots a specific virtual machine. **Caution:** Disruptive: restarts the guest. |
| `xe vm-list` | `xe vm-suspend uuid=<vm-uuid>` | Suspends a specific virtual machine. **Caution:** Disruptive: pauses the guest workload. |
| `xe vm-list` | `xe vm-resume uuid=<vm-uuid>` | Resumes a suspended virtual machine. **Caution:** Changes VM state. |

### Networking

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `xe network-list` | Lists all networks. |
| — | `xe vif-list vm-uuid=<vm-uuid>` | Lists virtual interfaces of a specific VM. |
| — | `xe pif-list host-uuid=<host-uuid>` | Lists physical interfaces on a host. |

### Storage Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `xe sr-list` | Lists all storage repositories. |
| — | `xe vdi-list sr-uuid=<sr-uuid>` | Lists virtual disk images in a storage repository. |
| — | `xe vbd-list vm-uuid=<vm-uuid>` | Lists virtual block devices of a VM. |

### VM Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| `xe vm-list` | `xe vm-export vm=<vm-name> filename=<file-path>` | Exports a VM to a file. **Caution:** Writes a VM export; check destination space and preserve existing files. |
| `xe vm-list` | `xe vm-import filename=<file-path>` | Imports a VM from a file. **Caution:** Creates VM and storage objects; inspect `xe sr-list` first. |
| — | `xe template-list` | Lists all VM templates. |
| `xe vm-list` | `xe vm-clone uuid=<vm-uuid> new-name-label=<new-name>` | Clones a VM. **Caution:** Creates VM and storage objects; inspect `xe sr-list` first. |
| `xe vm-list` | `xe vm-snapshot uuid=<vm-uuid> new-name-label=<snapshot-name>` | Takes a snapshot of a VM. **Caution:** Creates a recovery point and consumes storage; inspect `xe sr-list` first. |

### Resource and Pool Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `xe pool-list` | Lists all resource pools. |
| `xe vm-list` | `xe pool-param-set uuid=<pool-uuid> name-label=<new-name>` | Sets parameters for a resource pool. **Caution:** Changes pool configuration; inspect `xe pool-list` first. |
| `xe vm-list` | `xe host-param-set uuid=<host-uuid> name-label=<new-name>` | Sets parameters for a host. **Caution:** Changes host configuration; inspect `xe host-list` first. |

### Troubleshooting and Monitoring

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `xe task-list` | Lists all running tasks. |
| — | `xe event-list` | Lists recent events. |
| — | `xe log-display` | Displays the host log. |

## Troubleshooting workflow

1. Confirm the pool, host, VM UUID, and affected task.
2. Inspect host, VM, network, and storage lists before changing guest state.
3. Collect task status and the release-specific host logs with timestamps.
4. Compare VM placement, virtual interfaces, disks, and available host resources with the intended configuration.
5. Apply one targeted correction using the documentation for the installed XenServer release.
6. Verify guest and workload recovery, then record the configuration and recovery point.

## Official references

- [XenServer documentation](https://docs.xenserver.com/)
- [XenServer xe command-line interface](https://docs.xenserver.com/en-us/xenserver/9/command-line-interface)
