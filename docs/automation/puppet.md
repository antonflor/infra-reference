# Puppet Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for Puppet agent runs, manifests, modules, node management, and troubleshooting. The inherited examples span older Puppet tooling; confirm command availability for your installed release.

## Safety

Confirm the node and environment before applying a catalog. An agent test run can change packages, files, and services. Inspect configuration and reports first, and retain the previous manifests and module versions for recovery.

## Quick reference

### System Checks and Operations

| Inspect first | Command | Effect / caution |
|---|---|---|
| `puppet config print` | `puppet agent --test` | Runs a Puppet agent manually and applies the latest configuration. **Caution:** Applies a catalog and can change files, packages, and services. |
| `puppet config print` | `puppet agent --enable` | Enables the Puppet agent if it's been disabled. **Caution:** Resumes automatic catalog application. |
| `puppet config print` | `puppet agent --disable` | Temporarily disables the Puppet agent. **Caution:** Suspends automatic configuration enforcement. |
| — | `puppet config print <setting>` | Prints the value of a Puppet configuration setting. |

### Managing Puppet Code and Environments

| Inspect first | Command | Effect / caution |
|---|---|---|
| `puppet config print` | `puppet apply <manifest.pp>` | Applies a standalone Puppet manifest to the local system. **Caution:** Applies a manifest to the local host. |
| `puppet config print` | `puppet module install <module-name>` | Installs a module from the Puppet Forge. **Caution:** Changes installed modules. |
| — | `puppet module list` | Lists installed modules. |
| `puppet config print` | `puppet module upgrade <module-name>` | Upgrades a module to the latest version. **Caution:** Changes module versions and subsequent catalogs. |
| — | `puppet environment list` | Lists all available environments. |

### Node and Resource Management

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `puppet resource <resource-type> <resource-title>` | Manages a resource. |
| — | `puppet resource service` | Lists all services known to Puppet. |
| — | `puppet cert list` | Lists all pending certificate signing requests. |
| `puppet config print` | `puppet cert sign <certname>` | Signs a pending certificate request. **Caution:** Trusts a node certificate; verify the fingerprint and node identity. |
| `puppet config print` | `puppet node purge <node-name>` | Completely removes a node from PuppetDB and cleans up exported resources. **Caution:** Destructive: removes the node and exported resources. |

### Misc Puppet Tasks

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `puppet db export <file.tar.gz>` | Exports PuppetDB data to a file. |
| `puppet config print` | `puppet db import <file.tar.gz>` | Imports data into PuppetDB from a file. **Caution:** Changes PuppetDB data; preserve a verified backup first. |
| — | `puppet lookup <key> --node <node-name> --environment <environment>` | Looks up data in Hiera. |
| — | `puppet parser validate <manifest.pp>` | Validates the syntax of a Puppet manifest. |
| — | `puppet report show <report>` | Displays a specific report from PuppetDB. |

### Debugging and Troubleshooting

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `puppet agent --debug` | Runs the agent in debug mode for verbose output. |
| — | `puppet agent --fingerprint` | Prints the certificate fingerprint. |
| — | `puppet master --compile <node-name>` | Compiles a catalog for a specific node. |
| — | `puppet facts find <node-name>` | Retrieves facts from a specified node. |

## Troubleshooting workflow

1. Confirm the node, environment, Puppet release, and failing resource.
2. Inspect local configuration with `puppet config print` and review the most recent run report.
3. Collect agent and server logs with matching timestamps; inspect certificate and connectivity state.
4. Compare manifests, Hiera data, and module versions with the intended catalog.
5. Validate the manifest and review the expected changes before applying a correction to one node.
6. Verify the next report and service state; record the corrected configuration and rollback version.

## Official references

- [Puppet Core documentation](https://help.puppet.com/core/current/content/puppetcore/puppet_index.htm)
