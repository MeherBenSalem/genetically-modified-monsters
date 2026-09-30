# Genetically Modified Monsters

NightBeam Studio MultiLoader mod: experimental red mutant Creepers with dangerous mutations.

## Supported versions

| Version root | Minecraft | Loaders | Java |
| --- | --- | --- | --- |
| `1.20.1/` | 1.20.1 | Fabric, Forge | 17 |
| `1.21.1/` | 1.21.1 | Fabric, NeoForge | 21 |
| `26.2/` | 26.2 | Fabric, NeoForge | 25 |
| `26.3/` | 26.3 | Fabric, NeoForge | 25 |

## Variants

| Entity | Ability |
| --- | --- |
| Leap Creeper | High-jump ambush leaps |
| Climb Creeper | Scales walls like a spider |
| Swift Creeper | Faster movement and long follow range |
| Adaptive Creeper | Dodges attacks and avoids hazards |
| Overcharge Creeper | Explosion up to 2× charged Creeper power |
| Silent Creeper | Silent until detonation |
| Hunter Creeper | Persistent target-lock on players |

## Building

```powershell
cd 1.21.1
.\gradlew.bat build --no-daemon
```

Build all roots from the repository root (set `JAVA_HOME_17`, `JAVA_HOME_21`, `JAVA_HOME_25`):

```powershell
.\gradlew.bat buildAll --no-daemon
```

## License

Apache License 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
