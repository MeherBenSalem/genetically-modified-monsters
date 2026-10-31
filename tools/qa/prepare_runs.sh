#!/usr/bin/env bash
# Prepares dev run directories of a workspace for QA: server.properties (RCON on 25575), eula, the QA player as op,
# and client options that skip first-run screens.
#   tools/qa/prepare_runs.sh <workspace> <loader> [options.txt to copy]
# QA_PORT (default 25565) and QA_RCON (default 25575) pick the ports, so several dev servers can run at once.
set -eu
PORT=${QA_PORT:-25565}
RCON=${QA_RCON:-25575}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SERVER="$ROOT/$1/$2/runs/server"
CLIENT="$ROOT/$1/$2/runs/client"
mkdir -p "$SERVER" "$CLIENT"
cat > "$SERVER/server.properties" <<PROPS
allow-flight=true
broadcast-rcon-to-ops=false
difficulty=normal
enable-rcon=true
enforce-whitelist=false
force-gamemode=false
function-permission-level=2
gamemode=creative
level-name=qa_world
level-seed=spore-and-stem
max-tick-time=120000
motd=Spore and Stem QA
online-mode=false
op-permission-level=4
rcon.password=qa
rcon.port=$RCON
server-port=$PORT
simulation-distance=8
spawn-protection=0
view-distance=8
white-list=false
PROPS
echo "eula=true" > "$SERVER/eula.txt"
# Offline-mode UUID of the QA player.
UUID=$(python3 -c "import hashlib,uuid; h=bytearray(hashlib.md5(b'OfflinePlayer:Mycologist').digest()); h[6]=h[6]&0x0f|0x30; h[8]=h[8]&0x3f|0x80; print(uuid.UUID(bytes=bytes(h)))")
cat > "$SERVER/ops.json" <<OPS
[{"uuid": "$UUID", "name": "Mycologist", "level": 4, "bypassesPlayerLimit": false}]
OPS
if [ -n "${3:-}" ] && [ -f "$3" ]; then cp "$3" "$CLIENT/options.txt"; fi
# Forge dev servers: LAN advertising instantiates a client-only class, which the dev environment strips on the
# dedicated server and so crashes it right after start-up. New worlds copy this default.
if [ "$2" = forge ]; then
  mkdir -p "$SERVER/defaultconfigs"
  printf '[server]\n\tadvertiseDedicatedServerToLan = false\n' > "$SERVER/defaultconfigs/forge-server.toml"
fi
