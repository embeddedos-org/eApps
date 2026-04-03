# Cluster Demo Examples

Multi-node simulation configurations demonstrating EoSim's cluster capabilities.

## IoT Sensor-Gateway (`cluster.yml`)

A 3-node IoT cluster:

| Node | Platform | Role | Architecture |
|------|----------|------|-------------|
| `gateway` | `arm64` | Central gateway | ARM64 |
| `sensor-1` | `arm-mcu` | Temperature sensor | ARM Cortex-M |
| `sensor-2` | `arm-mcu` | Humidity sensor | ARM Cortex-M |

Nodes communicate via UART links at 115200 baud.

```bash
eosim run --cluster examples/cluster-demo/cluster.yml
```

## Automotive ECU (`automotive.yml`)

A 3-node automotive ECU cluster:

| Node | Platform | Role | Architecture |
|------|----------|------|-------------|
| `gateway` | `arm64` | Central ECU gateway | ARM64 |
| `body-ctrl` | `arm-mcu` | Body controller | ARM Cortex-M |
| `dashboard` | `arm-mcu` | Instrument cluster | ARM Cortex-M |

Nodes communicate via UART links at 115200 baud.

```bash
eosim run --cluster examples/cluster-demo/automotive.yml
```

## Cluster YAML Format

```yaml
name: my-cluster
nodes:
  - name: node-name
    platform: platform-name
    role: node-role

links:
  - type: uart
    from: node-a
    to: node-b
    config:
      baud: 115200
```

See [Platform Authoring Guide](../../docs/platform-authoring.md) for more on cluster definitions.
