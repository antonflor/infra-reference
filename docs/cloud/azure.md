# Microsoft Azure and Azure CLI Cheat Sheet

> **Applies to:** Azure CLI 2.x subscription and resource-group inspection
> **Last reviewed:** 2026-10-02

A reference for inspecting Azure account context and resource groups before troubleshooting or making a change. These read-only examples were checked against Microsoft CLI documentation; service-specific configuration requires the reference for the deployed service.

## Safety

Confirm the tenant, subscription, and resource group before operating. Specify the subscription explicitly when inspecting resources. Keep credentials and sensitive resource details out of shared command output; review backups and dependencies before any deletion.

## Quick reference

### Account context

```bash
az account list --output table
az account show --output json
az account show --subscription <subscription-id> --output json
```

Check the returned subscription ID and tenant ID against the intended environment.

### Resource groups

```bash
az group list --subscription <subscription-id> --output table
az group show --name <resource-group> --subscription <subscription-id> --output json
```

An empty list or missing group can indicate the wrong subscription or insufficient access. Inspect context and permissions before recreating a resource.

## Troubleshooting workflow

1. Confirm the affected tenant, subscription, resource group, resource, and failure time.
2. Inspect account context and resource-group state using the read-only commands above.
3. Collect the error code, correlation ID, and relevant service logs.
4. Compare the intended subscription, permissions, and resource configuration with the observed state.
5. Apply the least disruptive correction using the matching Azure service documentation.
6. Verify the original operation or service and record the change and rollback state.

## Official references

- [Azure CLI account reference](https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-latest)
- [Azure CLI resource-group reference](https://learn.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest)
