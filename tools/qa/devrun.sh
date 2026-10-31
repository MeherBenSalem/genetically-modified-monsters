#!/usr/bin/env bash
# Start or stop dev servers/clients for QA under Xvfb with software rendering.
#   tools/qa/devrun.sh start-server <workspace> <loader>
#   tools/qa/devrun.sh start-client <workspace> <loader>
#   tools/qa/devrun.sh stop-client | stop-server [<workspace>]
# Logs go to $QA_LOGS (default /tmp/spore-and-stem-qa). Start Xvfb on $DISPLAY (default :1) before the client:
#   Xvfb :1 -screen 0 1920x1080x24 &
set -u
LOGS=${QA_LOGS:-/tmp/spore-and-stem-qa}
mkdir -p "$LOGS"
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
# Gradle runs on the workspace's Java: 21 for 1.21.1 (override with QA_JAVA_HOME).
case "${2:-}" in
  1.20.1) default_java=$(ls -d /usr/lib/jvm/java-17-openjdk-amd64 /opt/jdks/jdk-17* 2>/dev/null | head -1) ;;
  1.21.1) default_java=$(ls -d /usr/lib/jvm/java-21-openjdk-amd64 /opt/jdks/jdk-21* 2>/dev/null | head -1) ;;
  *) default_java=$(ls -d /opt/jdks/jdk-25* /usr/lib/jvm/java-21-openjdk-amd64 2>/dev/null | head -1) ;;
esac
JAVA_HOME=${QA_JAVA_HOME:-$default_java}
export JAVA_HOME
case "$1" in
  start-server)
    cd "$ROOT/$2" && nohup ./gradlew ":$3:runServer" --no-daemon > "$LOGS/$3-server.log" 2>&1 &
    ;;
  start-client)
    export DISPLAY=${DISPLAY:-:1} LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe ${QA_CLIENT_ENV:-}
    cd "$ROOT/$2" && nohup ./gradlew ":$3:runQaClient" --no-daemon > "$LOGS/$3-client.log" 2>&1 &
    ;;
  stop-client|stop-server)
    # Only java processes are considered, so this never matches the calling shell.
    want=$([ "$1" = stop-client ] && echo 'KnotClient|clientQaClient|runQaClient|--quickPlayMultiplayer' || echo 'KnotServer|runServer|neoforgeserver|--nogui')
    for pid in $(pgrep -x java); do
      cmd=$(tr '\0' ' ' < "/proc/$pid/cmdline")
      if echo "$cmd" | grep -qE "$want" && { [ -z "${2:-}" ] || echo "$cmd $(readlink "/proc/$pid/cwd")" | grep -q "/$2/"; }; then kill "$pid"; fi
    done
    ;;
esac
