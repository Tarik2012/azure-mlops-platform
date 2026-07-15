# Azure ML assets

This directory contains deployment-neutral Azure ML asset definitions. Nothing in
this folder creates Azure resources until a user explicitly submits it with the
Azure CLI or SDK.

## Structure

- `environments/`: reproducible runtime definitions and Conda dependencies.
- `jobs/`: command-job definitions that run project training entrypoints.
- `endpoints/`: reserved for future managed online endpoint and deployment assets.

The `train_iris.yml` job expects environment `sklearn-mlflow:1` and compute
`cpu-cluster`. Register the environment and provision compute before submission.
