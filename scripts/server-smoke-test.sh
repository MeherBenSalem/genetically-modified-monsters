#!/usr/bin/env bash
# Boots a dev server for one Minecraft version and loader and proves the mod works at runtime, not only compiles:
# places every Spore & Stem configured feature with /place feature on a prepared pad near spawn, summons every
# Spore & Stem entity, gives a mob Mycosis, runs for ~600 ticks and stops.
# Fails on a crash report, a mixin error, a load or registry error mentioning the mod, a failed /place, a summon
# that did not happen, or when the OK marker never shows up.
#   usage: scripts/server-smoke-test.sh <26.2|26.3|...> <fabric|neoforge>
set -u
VERSION="$1"; LOADER="$2"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/$VERSION"
MOD=spore_and_stem
NS=sns_smoke
RUN="$LOADER/runs/server"
rm -rf "$RUN/world" "$RUN/crash-reports" "$RUN/logs"
PACK="$RUN/world/datapacks/$NS"
mkdir -p "$PACK"
echo "eula=true" > "$RUN/eula.txt"
cat > "$RUN/server.properties" <<PROPS
online-mode=false
function-permission-level=4
spawn-protection=0
view-distance=6
simulation-distance=6
level-seed=20261123
initial-enabled-packs=vanilla,file/$NS
PROPS

# pack.mcmeta as valid JSON, with the same format range as the mod's own pack (26.x uses min_format/max_format).
python3 - common/src/main/resources/pack.mcmeta "$PACK/pack.mcmeta" <<'PY'
import json, sys
src = json.load(open(sys.argv[1]))["pack"]
pack = {"description": "Spore & Stem smoke test"}
for key in ("pack_format", "min_format", "max_format", "supported_formats"):
    if key in src:
        pack[key] = src[key]
json.dump({"pack": pack}, open(sys.argv[2], "w"))
PY
cat "$PACK/pack.mcmeta"; echo

# Configured features live in worldgen/configured_feature up to 26.2 and in worldgen/feature from 26.3.
DATA="common/src/generated/resources/data/$MOD/worldgen"
if [ -d "$DATA/configured_feature" ]; then FEATURE_DIR="$DATA/configured_feature"; else FEATURE_DIR="$DATA/feature"; fi
FEATURES="$(ls "$FEATURE_DIR" | sed 's/\.json$//')"
ENTITIES="$(grep -o 'register("[a-z_]*"' common/src/main/java/com/nightbeam/sporeandstem/registry/ModEntities.java | sed 's/register("//; s/"//')"
FEATURE_COUNT=$(echo "$FEATURES" | wc -w)
ENTITY_COUNT=$(echo "$ENTITIES" | wc -w)
echo "Features ($FEATURE_COUNT): $FEATURES"
echo "Entities ($ENTITY_COUNT): $ENTITIES"

# One 25x25 pad per feature on a 32-block grid around spawn, high above the terrain: dirt, grass on top, air above.
SLOTS=()
for gz in -64 -32 0 32 64; do for gx in -64 -32 0 32 64; do SLOTS+=("$gx $gz"); done; done

pad() { # x z
  echo "fill $(($1-12)) 97 $(($2-12)) $(($1+12)) 98 $(($2+12)) minecraft:dirt"
  echo "fill $(($1-12)) 99 $(($2-12)) $(($1+12)) 99 $(($2+12)) minecraft:grass_block"
  echo "fill $(($1-12)) 100 $(($2-12)) $(($1+12)) 125 $(($2+12)) minecraft:air"
}

FN="$PACK/data/$NS"
for dir in function functions; do
  mkdir -p "$FN/$dir" "$PACK/data/minecraft/tags/$dir"
  echo "{\"values\":[\"$NS:start\"]}" > "$PACK/data/minecraft/tags/$dir/load.json"
  {
    echo 'scoreboard objectives add sns dummy'
    echo 'forceload add -80 -80 80 80'
    echo 'say SNS_SMOKE_LOADED'
    echo "schedule function $NS:build 300t"
  } > "$FN/$dir/start.mcfunction"

  # Build every pad (and what each feature needs around it), then place a tick later.
  {
    i=0
    for f in $FEATURES; do
      set -- ${SLOTS[$i]}; x=$1; z=$2
      pad "$x" "$z"
      case "$f" in
        mycelial_veil*) echo "fill $((x-6)) 106 $((z-6)) $((x+6)) 106 $((z+6)) minecraft:stone" ;;
        shelf_fungus*)
          for dx in -6 -4 -2 0 2 4 6; do for dz in -6 -4 -2 0 2 4 6; do
            [ "$dx" = 0 ] && [ "$dz" = 0 ] && continue
            echo "fill $((x+dx)) 100 $((z+dz)) $((x+dx)) 109 $((z+dz)) minecraft:oak_log"
          done; done ;;
        ore_*) echo "fill $((x-4)) 100 $((z-4)) $((x+4)) 108 $((z+4)) minecraft:dirt" ;;
      esac
      i=$((i + 1))
    done
    set -- ${SLOTS[24]}; pad "$1" "$2"
    echo 'say SNS_SMOKE_BUILT'
    echo "schedule function $NS:run 20t"
  } > "$FN/$dir/build.mcfunction"

  {
    i=0
    for f in $FEATURES; do
      set -- ${SLOTS[$i]}; x=$1; z=$2
      case "$f" in
        mycelial_veil*|ore_*) y=104 ;;
        *) y=100 ;;
      esac
      echo "scoreboard players set #r sns 0"
      echo "execute store success score #r sns run place feature $MOD:$f $x $y $z"
      echo "execute if score #r sns matches 1 run say SNS_PLACED $f"
      echo "execute unless score #r sns matches 1 run say SNS_PLACE_FAILED $f"
      i=$((i + 1))
    done
    # Every entity on the last pad, then a sick zombie and pig for Mycosis.
    set -- ${SLOTS[24]}; x=$1; z=$2
    dx=-10
    for e in $ENTITIES; do
      echo "execute store success score #r sns run summon $MOD:$e $((x+dx)) 101 $z {Tags:[\"sns_smoke\"],PersistenceRequired:1b}"
      echo "execute if score #r sns matches 1 run say SNS_SUMMONED $e"
      echo "execute unless score #r sns matches 1 run say SNS_SUMMON_FAILED $e"
      dx=$((dx + 2))
    done
    echo "summon minecraft:zombie $x 101 $((z+8)) {Tags:[\"sns_smoke\",\"sns_sick\"],PersistenceRequired:1b}"
    echo "summon minecraft:pig $((x+3)) 101 $((z+8)) {Tags:[\"sns_smoke\",\"sns_sick\"],PersistenceRequired:1b}"
    echo "execute store success score #r sns run effect give @e[tag=sns_sick] $MOD:mycosis 60 1"
    echo "execute if score #r sns matches 1 run say SNS_MYCOSIS_APPLIED"
    echo "execute unless score #r sns matches 1 run say SNS_MYCOSIS_FAILED"
    echo 'say SNS_SMOKE_RAN'
    echo "schedule function $NS:finish 600t"
  } > "$FN/$dir/run.mcfunction"

  {
    echo 'execute if entity @e[tag=sns_sick] run say SNS_SICK_ALIVE'
    echo 'kill @e[tag=sns_smoke]'
    echo 'say SNS_SMOKE_OK'
    echo 'stop'
  } > "$FN/$dir/finish.mcfunction"
done

LOG="$ROOT/server-smoke-$VERSION-$LOADER.log"
./gradlew ":$LOADER:runServer" --stacktrace < /dev/null > "$LOG" 2>&1 &
PID=$!
CRASH='This crash report has been saved|Encountered an unexpected exception|Failed to start the minecraft server|Mixin apply.*failed|InvalidInjectionException|MixinTransformerError|Mixin.*(error|failed)'
result=timeout
for _ in $(seq 1 240); do
  sleep 5
  if grep -q "SNS_SMOKE_OK" "$LOG"; then result=ok; break; fi
  if grep -q -E "$CRASH" "$LOG"; then result=crash; break; fi
  if ! kill -0 $PID 2>/dev/null; then result=exited; break; fi
done
sleep 10
pkill -P $PID 2>/dev/null; kill $PID 2>/dev/null; wait $PID 2>/dev/null

echo "===== markers"
grep -n -E "SNS_|Found new data pack|Loaded [0-9]+ recipes" "$LOG" | head -80
for f in "$RUN"/crash-reports/*.txt; do [ -f "$f" ] && { echo "=== $f"; head -100 "$f"; }; done
echo "===== errors and warnings"
grep -n -E "ERROR|Exception|Caused by|[Mm]ixin.*(fail|error)|Failed to|Couldn't|Unknown|missing" "$LOG" | grep -v -E "Download|Task :" | head -80
echo "Result: $result"

fail=0
[ "$result" = ok ] || { echo "::error::server did not reach SNS_SMOKE_OK ($result)"; fail=1; }
grep -q -E "$CRASH" "$LOG" && { echo "::error::crash or mixin error"; fail=1; }
grep -q "SNS_SMOKE_RAN" "$LOG" || { echo "::error::the smoke function never ran"; fail=1; }
if grep -n -E "SNS_PLACE_FAILED|SNS_SUMMON_FAILED|SNS_MYCOSIS_FAILED|Failed to place" "$LOG"; then echo "::error::a /place, /summon or /effect failed"; fail=1; fi
placed=$(grep -c "SNS_PLACED" "$LOG"); summoned=$(grep -c "SNS_SUMMONED" "$LOG")
echo "Placed $placed of $FEATURE_COUNT features, summoned $summoned of $ENTITY_COUNT entities"
[ "$placed" -ge "$FEATURE_COUNT" ] || { echo "::error::not every feature was placed"; fail=1; }
[ "$summoned" -ge "$ENTITY_COUNT" ] || { echo "::error::not every entity was summoned"; fail=1; }
# Load and registry errors that mention the mod (datapack elements, registries, tags, codecs).
if grep -n -E "(ERROR|WARN|Exception|Caused by|Failed|Couldn't|Unknown|Errors in)" "$LOG" | grep -i -E "spore_and_stem|sporeandstem|$NS"; then
  echo "::error::load or registry error mentioning the mod"; fail=1
fi
exit $fail
