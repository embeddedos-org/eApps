# EoSim Examples

This directory contains example configurations for EoSim.

## Cluster Demos

The `cluster-demo/` directory contains multi-node simulation examples:

- **`cluster.yml`** — IoT sensor-gateway cluster (3 nodes: 1 ARM64 gateway + 2 ARM MCU sensors)
- **`automotive.yml`** — Automotive ECU cluster (3 nodes: gateway + body-controller + dashboard)

### Running a Cluster Demo

```bash
# IoT sensor-gateway cluster
eosim run --cluster examples/cluster-demo/cluster.yml

# Automotive ECU cluster
eosim run --cluster examples/cluster-demo/automotive.yml
```

## Creating Your Own Examples

See the [Platform Authoring Guide](../docs/platform-authoring.md) for details on creating platform configs and cluster definitions.
