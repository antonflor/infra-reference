# Pacemaker Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for Pacemaker high-availability cluster inspection, resources, nodes, constraints, and fencing using `pcs`. Command syntax varies by `pcs` and Pacemaker release.

## Safety

Inspect cluster membership, quorum, resource placement, and fencing before changing cluster state. Stopping services, deleting resources, or altering fencing can interrupt service or compromise recovery. Preserve the cluster configuration and use the release-specific recovery procedure.

## Quick reference

### Key Features of Pacemaker:

1. **Resource Management**: Manages various types of services as resources.
2. **Cluster Management**: Detects and responds to node failures.
3. **Failover and Recovery**: Automatically relocates services during failures.
4. **Resource Grouping**: Groups resources for collective management.
5. **Constraints**: Supports various constraints for resource management.
6. **STONITH**: Implements fencing mechanism for cluster safety.
7. **Integration with Corosync**: Often used with Corosync for messaging and membership.

### Cluster Status and Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs status` | Displays the current status of the cluster. |
| `pcs status` | `pcs cluster start --all` | Starts all cluster services on all nodes. **Caution:** Starts services across the cluster. |
| `pcs status` | `pcs cluster stop --all` | Stops all cluster services on all nodes. **Caution:** Disruptive: stops cluster services across all nodes. |
| `pcs status` | `pcs cluster enable --all` | Enables cluster services to start at boot on all nodes. **Caution:** Changes cluster startup behavior. |
| `pcs status` | `pcs cluster disable --all` | Disables cluster services from starting at boot. **Caution:** Disables cluster startup at boot. |

### Resource Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs resource show` | Lists all cluster resources. |
| `pcs status` | `pcs resource create <resource-id> <agent> <options>` | Creates a new cluster resource. **Caution:** Changes the cluster resource configuration. |
| `pcs status` | `pcs resource delete <resource-id>` | Deletes a cluster resource. **Caution:** Destructive: removes the resource definition and can stop service. |
| `pcs status` | `pcs resource manage <resource-id>` | Manages a resource (enables cluster management). **Caution:** Resumes cluster control of the resource. |
| `pcs status` | `pcs resource unmanage <resource-id>` | Unmanages a resource (disables cluster management). **Caution:** Suspends cluster control of the resource. |

### Node Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs status nodes` | Shows the status of all nodes in the cluster. |
| `pcs status` | `pcs cluster standby <node>` | Sets a cluster node to standby mode. **Caution:** Evacuates resources from the node. |
| `pcs status` | `pcs cluster unstandby <node>` | Removes a cluster node from standby mode. **Caution:** Allows resource placement on the node. |
| — | `pcs cluster cib` | Outputs the current cluster configuration. |

### Constraint Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs constraint list` | Lists all constraints in the cluster. |
| `pcs status` | `pcs constraint create <constraint-options>` | Creates a new constraint. **Caution:** Changes resource placement. |
| `pcs status` | `pcs constraint remove <constraint-id>` | Removes a constraint. **Caution:** Removes placement constraints. |

### Cluster Configuration

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs property list` | Lists all cluster properties. |
| `pcs status` | `pcs property set <property-name>=<value>` | Sets a cluster property. **Caution:** Changes cluster behavior; review quorum and fencing effects. |
| — | `pcs stonith show` | Displays STONITH (fencing) devices and status. |
| `pcs status` | `pcs stonith create <stonith-id> <agent> <options>` | Creates a new STONITH device. **Caution:** Changes fencing configuration. |
| `pcs status` | `pcs stonith delete <stonith-id>` | Deletes a STONITH device. **Caution:** Destructive: removes a fencing definition and can compromise recovery. |

### Troubleshooting and Logs

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `pcs status failures` | Shows all failed actions in the cluster. |
| — | `corosync-cfgtool -s` | Displays the status of the Corosync ring. |
| — | `crm_mon -1` | Displays a one-time status of the current cluster. |

### Tips for Using Pacemaker

- **Regular Backups**: Regularly backup your cluster configuration.
- **Monitoring**: Continuously monitor cluster health and performance.
- **Documentation**: Maintain detailed documentation of your cluster setup.
- **Testing**: Regularly test failover and recovery procedures.

## Troubleshooting workflow

1. Confirm the affected resource, node, time, and whether the failure is cluster-wide.
2. Inspect `pcs status`, membership, quorum, resource placement, and fencing without changing state.
3. Collect Pacemaker and Corosync logs and failed-action timestamps.
4. Compare resource definitions, constraints, and node configuration with the intended state.
5. Use the release-specific procedure for the smallest correction; do not disable fencing to hide a failure.
6. Verify resource and client health, then record configuration backups and recovery actions.

## Official references

- [ClusterLabs documentation](https://clusterlabs.org/projects/pacemaker/doc/)
