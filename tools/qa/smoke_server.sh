#!/usr/bin/env bash
# Boots a dedicated server for one loader on a FRESH world, waits until it is ready (or fails), then stops it.
#   tools/qa/smoke_server.sh <fabric|neoforge|forge> [workspace, default 1.21.1] [log-file]
# Exit code 0 only if the server reached "Done" and the log has no errors from Spore & Stem, data loading
# (recipes, loot tables, tags, advancements, worldgen) or biome modifiers. Uses QA_PORT/QA_RCON if set.
set -u
loader="${1:?fabric, neoforge or forge}"
ws="${2:-1.21.1}"
log="${3:-/tmp/spore_and_stem_smoke_${ws}_${loader}.log}"
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../../$ws" && pwd)"
"$here/prepare_runs.sh" "$ws" "$loader" >/dev/null
# Gradle runs on the workspace's Java (java_version in its gradle.properties), as in devrun.sh.
jv=$(sed -n 's/^java_version=//p' "$root/gradle.properties")
export JAVA_HOME="${QA_JAVA_HOME:-$(ls -d /usr/lib/jvm/java-${jv}-openjdk-amd64 /opt/jdks/jdk-${jv}* 2>/dev/null | head -1)}"
rundir="$root/$loader/runs/server"
sed -i 's/^level-name=.*/level-name=smoke_world/' "$rundir/server.properties"
rm -rf "$rundir/smoke_world"
cd "$root"
./gradlew ":${loader}:runServer" --no-daemon > "$log" 2>&1 &
pid=$!
deadline=$((SECONDS + 1500))
status=1
while kill -0 "$pid" 2>/dev/null; do
  if grep -qE 'Done \([0-9.]+s\)!' "$log"; then status=0; break; fi
  if grep -qE 'Crash report|Exception in server tick loop|Failed to start the minecraft server|BUILD FAILED' "$log"; then break; fi
  if (( SECONDS > deadline )); then echo "timeout" >> "$log"; break; fi
  sleep 3
done
sleep 2
for p in $(pgrep -x java); do
  if tr '\0' ' ' < "/proc/$p/cmdline" | grep -qE 'KnotServer|neoforgeserver|--nogui' && readlink "/proc/$p/cwd" | grep -q "$root/$loader"; then kill "$p"; fi
done
kill "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
sed -i 's/^level-name=.*/level-name=qa_world/' "$rundir/server.properties"

errors=$(grep -E '/(ERROR|FATAL)\]|Couldn.t parse|Failed to (load|parse)|Unknown (item|block|tag|entity)|Parsing error|validation problem|spore_and_stem.*(WARN|warn)' "$log" \
  | grep -v -E 'Realms|realms|No data fixer registered' | head -60)
if [[ -n "$errors" ]]; then
  echo "---- errors ----"; echo "$errors"; status=1
fi
grep -E 'is growing|Done \(' "$log" | head -5
echo "smoke($ws $loader) status=$status log=$log"
exit $status
