# Cost and Safety Guidance

## Purpose

This document explains the cost and safety controls used for the manual Azure deployment of the `azure-mlops-platform` API in a development context.

The deployment was intentionally temporary. After validation, the Resource Group was deleted so that all associated Azure resources were removed together.

## Why Azure Resources Can Generate Cost

Even small development environments can create billable consumption. In this project, the relevant cost considerations were:

- Azure Container Registry storage and operations
- Azure Container Apps environment and runtime usage
- Container App compute and memory allocation
- Log and platform retention depending on configuration
- Any additional dependent services that might be added in future iterations

The practical lesson is straightforward: a successful test deployment should not be left running without a reason.

## Why Deleting the Resource Group Is the Safest Cleanup Method in Dev

Deleting the Resource Group is the safest cleanup method for a temporary development deployment because it removes the full resource boundary in one action.

Benefits:

- Prevents orphaned resources from being left behind.
- Reduces the chance of forgetting a billable component.
- Keeps cleanup simple and auditable.
- Matches the way the environment was provisioned: all resources belonged to the same development scope.

For this project, deleting `rg-azure-mlops-platform-dev` removed the Azure Container Registry, Managed Identity, Container Apps Environment, Container App, and related configuration within that group.

## Historical Verification Command

The cleanup verification command used for this deployment was:

```bash
az group exists --name rg-azure-mlops-platform-dev
```

Expected result after deletion:

```text
false
```

Validated result for this exercise:

```text
false
```

## Cost Safety Checklist

- Create development resources inside a dedicated Resource Group.
- Use explicit development naming such as `*-dev`.
- Keep sizing conservative for non-production tests.
- Limit scale settings for the Container App.
- Use temporary resources only for the duration of validation.
- Confirm the deployment with targeted endpoint tests.
- Delete the Resource Group after the test window closes.
- Verify deletion with `az group exists`.

## What Not to Leave Running

In a temporary development environment, do not leave these active longer than necessary:

- Azure Container Registry instances created only for a short exercise
- Container Apps Environments created only for a short exercise
- Public Container Apps that are no longer under test
- Unused images and revisions that have no remaining validation value
- Identity and role bindings created only for a disposable development run

## Why This Deployment Was Cost-Safe

This deployment followed good development hygiene:

- The environment was intentionally scoped to one Resource Group.
- The Container App used a modest runtime profile.
- The exercise stopped at inference validation, not long-lived production hosting.
- Cleanup was completed successfully.
- Post-cleanup verification confirmed that the Resource Group no longer existed.

## Dev vs Production Cost Considerations

### Development

Development environments should prioritize:

- temporary lifetimes
- small SKUs
- minimum replica counts
- rapid teardown
- simple observability sufficient for debugging

### Production

Production environments usually require:

- higher availability and resilience
- stronger monitoring and alerting
- retention policies
- security hardening
- controlled scaling policies
- more durable artifact and infrastructure strategies

These production requirements increase cost but are justified by uptime, supportability, and governance needs.

## Safety Recommendation

For manual Azure exercises, treat Resource Group deletion as a required closing task, not an optional cleanup step. That approach is the clearest protection against accidental ongoing spend in development subscriptions.
