# Puppet Command Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for Puppet agent runs, manifests, modules, node management, and troubleshooting. Examples target Puppet 7 and 8 and the compatible OpenVox releases; confirm command availability for your installed release.

## Safety

Confirm the node and environment before applying a catalog. An agent test run can change packages, files, and services. Inspect configuration and reports first, and retain the previous manifests and module versions for recovery.

## Quick reference

### Release and packaging notes

- These commands target Puppet 7 and 8. `puppet cert` and `puppet master` were removed in Puppet 6; certificate work moved to `puppetserver ca` and catalog compilation to `puppet catalog compile`.
- Perforce no longer publishes open-source Puppet packages; current Perforce builds ship as Puppet Core or Puppet Enterprise under a commercial agreement. OpenVox is the community-maintained, Apache-2.0 continuation and keeps the same `puppet` command, language, and `/etc/puppetlabs` layout.
- `puppet node purge` and PuppetDB export or import are Puppet Enterprise or PuppetDB-client commands and are absent from a plain agent install.

### Agent runs

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `puppet config print <setting> --section agent` | Prints the effective value of a setting. |
| — | `puppet agent --test --noop` | Compiles and reports what would change without applying it. |
| `puppet agent --test --noop` | `puppet agent --test` | Runs the agent once in the foreground. **Caution:** Applies the catalog and can change files, packages, and services. |
| `puppet agent --test --noop` | `puppet agent --test --environment <environment>` | Runs once against another environment. **Caution:** Applies that environment's catalog. |
| — | `puppet agent --disable "<reason>"` | Pauses agent runs and records why. **Caution:** Suspends configuration enforcement until re-enabled. |
| `puppet agent --test --noop` | `puppet agent --enable` | Resumes agent runs. **Caution:** The next run applies any pending catalog changes. |
| — | `puppet agent --test --debug` | Runs once with debug output. **Caution:** Still applies the catalog; add `--noop` to inspect only. |

### Code, modules, and data

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `puppet parser validate <manifest.pp>` | Checks manifest syntax. |
| `puppet apply --noop <manifest.pp>` | `puppet apply <manifest.pp>` | Applies a standalone manifest locally. **Caution:** Changes the local host. |
| — | `puppet module list --tree` | Lists installed modules and dependencies. |
| `puppet module list` | `puppet module install <author>-<module> --version <version>` | Installs a Forge module. **Caution:** Changes the modulepath; environments managed by r10k or Code Manager should change the `Puppetfile` instead. |
| `puppet module list` | `puppet module upgrade <author>-<module>` | Upgrades a module. **Caution:** Changes subsequent catalogs. |
| — | `puppet lookup <key> --node <certname> --environment <environment> --explain` | Resolves a Hiera key and shows which layer supplied it. |
| — | `puppet catalog compile <certname> --environment <environment>` | Compiles a catalog on the server without applying it. |

### Resources and facts

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `puppet resource <type> <title>` | Shows the current state of a resource as Puppet code. |
| — | `puppet resource service` | Lists services known to the service provider. |
| `puppet resource <type> <title>` | `puppet resource <type> <title> <attribute>=<value>` | Changes a resource immediately. **Caution:** Bypasses the catalog; the next agent run may revert it. |
| — | `puppet facts show` | Prints local facts. |
| — | `facter <fact>` | Prints one fact, such as `facter os.release`. |

### Certificates

Run `puppetserver ca` on the CA server. Run `puppet ssl` on the agent.

| Inspect first | Command | Effect / caution |
|---|---|---|
| — | `puppetserver ca list` | Lists pending certificate requests. |
| — | `puppetserver ca list --all` | Lists signed, revoked, and pending certificates. |
| `puppetserver ca list` | `puppetserver ca sign --certname <certname>` | Signs a pending request. **Caution:** Trusts the node; compare the fingerprint with `puppet agent --fingerprint` on the agent first. |
| `puppetserver ca list --all` | `puppetserver ca clean --certname <certname>` | Revokes and removes a node certificate. **Caution:** The node cannot check in until it is re-enrolled. |
| — | `puppet agent --fingerprint` | Prints the agent certificate or request fingerprint. |
| — | `puppet ssl verify` | Checks that the agent's certificate, key, and CA chain are usable. |
| `puppet ssl verify` | `puppet ssl clean` | Deletes the agent's local certificates. **Caution:** Requires a new signing on the CA. |

## Troubleshooting workflow

1. Confirm the node, environment, Puppet release, and failing resource.
2. Inspect local configuration with `puppet config print` and review the most recent run report.
3. Collect agent and server logs with matching timestamps; inspect certificate and connectivity state.
4. Compare manifests, Hiera data, and module versions with the intended catalog.
5. Validate the manifest and review the expected changes before applying a correction to one node.
6. Verify the next report and service state; record the corrected configuration and rollback version.

## Official references

- [Puppet Core documentation](https://help.puppet.com/core/current/content/puppetcore/puppet_index.htm)
- [OpenVox project](https://voxpupuli.org/openvox/)
