# Pacemaker Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for Pacemaker high-availability cluster inspection, resources, nodes, constraints, and fencing using `pcs`. Command syntax varies by `pcs` and Pacemaker release. See [Corosync](corosync.md) for the membership and quorum layer.

## Safety

Inspect cluster membership, quorum, resource placement, and fencing before changing cluster state. Stopping services, deleting resources, or altering fencing can interrupt service or compromise recovery. Preserve the cluster configuration and use the release-specific recovery procedure.

## Quick reference

### Release notes

Syntax below is for `pcs` 0.10 and 0.11 (RHEL 8 and 9 families, current Debian and Ubuntu). Older forms such as `pcs resource show`, `pcs stonith show`, `pcs cluster standby`, and `pcs property list` were removed or renamed; on SUSE, the equivalent tool is `crmsh`.

### Cluster status and lifecycle

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs status --full` | Shows nodes, resources, failed actions, and daemon state. |
| — | `pcs quorum status` | Shows votes, quorum, and membership. |
| — | `crm_mon -1r` | One-shot status including inactive resources. |
| `pcs status` | `pcs cluster start --all` | Starts Corosync and Pacemaker on every node. **Caution:** Resources start as soon as quorum forms. |
| `pcs status` | `pcs cluster stop --all` | Stops cluster services everywhere. **Caution:** Disruptive: stops every managed resource. |
| `pcs status` | `pcs cluster enable --all` | Starts cluster services at boot. **Caution:** A rebooted node rejoins automatically. |
| `pcs status` | `pcs cluster disable --all` | Stops cluster services starting at boot. **Caution:** Nodes stay out of the cluster after reboot until started. |

### Resources

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs resource status` | Lists resources and where they run. |
| — | `pcs resource config <resource-id>` | Shows a resource definition and its operations. |
| — | `pcs resource describe <agent>` | Lists the parameters an agent accepts. |
| `pcs resource status` | `pcs resource create <resource-id> <agent> <options>` | Creates a resource. **Caution:** It starts immediately unless created with `--disabled`. |
| `pcs resource config <resource-id>` | `pcs resource update <resource-id> <option>=<value>` | Changes resource parameters. **Caution:** Many changes restart the resource. |
| `pcs resource status` | `pcs resource move <resource-id> <node>` | Moves a resource. **Caution:** Disruptive; on `pcs` 0.10 it leaves a location constraint that `pcs resource clear <resource-id>` removes. |
| `pcs resource status` | `pcs resource disable <resource-id>` | Stops a resource and keeps it stopped. **Caution:** Disruptive. |
| `pcs resource status` | `pcs resource enable <resource-id>` | Allows the resource to start again. |
| `pcs resource status` | `pcs resource unmanage <resource-id>` | Stops Pacemaker from starting, stopping, or recovering the resource. **Caution:** No failover while unmanaged. |
| `pcs resource status` | `pcs resource manage <resource-id>` | Returns the resource to cluster control. **Caution:** Pacemaker acts on the state it finds. |
| `pcs resource failcount show <resource-id>` | `pcs resource cleanup <resource-id>` | Clears failure history so the resource can be retried. **Caution:** Removes diagnostic evidence and can trigger a start. |
| `pcs resource config <resource-id>` | `pcs resource delete <resource-id>` | Deletes a resource. **Caution:** Destructive: stops the service and removes its definition and constraints. |

### Nodes

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs status nodes` | Shows online, standby, and offline nodes. |
| `pcs status` | `pcs node standby <node>` | Puts a node in standby. **Caution:** Moves its resources elsewhere. |
| `pcs status` | `pcs node unstandby <node>` | Returns a node to service. **Caution:** Resources can move back depending on stickiness. |
| `pcs status` | `pcs node maintenance <node>` | Leaves resources running but unmanaged on that node. **Caution:** No recovery for those resources. |
| `pcs status` | `pcs node unmaintenance <node>` | Ends node maintenance. |

### Constraints

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs constraint config --full` | Lists constraints with IDs (`pcs constraint --full` on 0.10). |
| `pcs constraint config` | `pcs constraint location <resource-id> prefers <node>=<score>` | Adds a location preference. **Caution:** Can move the resource. |
| `pcs constraint config` | `pcs constraint order <first-resource> then <second-resource>` | Adds a start order. **Caution:** Can restart dependent resources. |
| `pcs constraint config` | `pcs constraint colocation add <resource> with <other-resource> <score>` | Keeps resources together or apart. **Caution:** Can move resources. |
| `pcs constraint config --full` | `pcs constraint delete <constraint-id>` | Removes a constraint. **Caution:** Placement is recalculated. |

### Properties, fencing, and configuration backup

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs property config` | Lists cluster properties (`pcs property list` on 0.10). |
| `pcs property config` | `pcs property set <property>=<value>` | Sets a cluster property. **Caution:** Review quorum and fencing effects; never set `stonith-enabled=false` on a cluster with shared data. |
| — | `pcs stonith status` | Shows fence devices and their state. |
| — | `pcs stonith config` | Shows fence device definitions. |
| `pcs stonith status` | `pcs stonith create <stonith-id> <agent> <options>` | Creates a fence device. **Caution:** Changes fencing behavior. |
| `pcs stonith config` | `pcs stonith delete <stonith-id>` | Deletes a fence device. **Caution:** Destructive: can leave nodes unfenceable. |
| `pcs status` | `pcs stonith fence <node>` | Fences a node now. **Caution:** Destructive: power-cycles or isolates the node. |
| — | `pcs cluster cib > <file.xml>` | Saves the live CIB for review or rollback. |
| — | `pcs config backup <file>` | Archives cluster configuration files from all nodes. |

### Logs and membership

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `corosync-cfgtool -s` | Shows link status for the local node. |
| — | `corosync-quorumtool -s` | Shows quorum state as Corosync sees it. |
| — | `journalctl -u pacemaker -u corosync --since "<time>"` | Reads daemon logs around an event. |
| — | `crm_verify -L -V` | Checks the live configuration for errors and warnings. |

## Troubleshooting workflow

1. Confirm the affected resource, node, time, and whether the failure is cluster-wide.
2. Inspect `pcs status`, membership, quorum, resource placement, and fencing without changing state.
3. Collect Pacemaker and Corosync logs and failed-action timestamps.
4. Compare resource definitions, constraints, and node configuration with the intended state.
5. Use the release-specific procedure for the smallest correction; do not disable fencing to hide a failure.
6. Verify resource and client health, then record configuration backups and recovery actions.

## Official references

- [ClusterLabs documentation](https://clusterlabs.org/projects/pacemaker/doc/)
