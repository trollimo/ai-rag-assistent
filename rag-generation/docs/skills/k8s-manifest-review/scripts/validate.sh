#!/usr/bin/env bash
# Грубая статическая проверка манифестов на отсутствие лимитов/probes.
# Использование: ./validate.sh <путь-к-манифестам>
set -euo pipefail

target="${1:?Укажите путь к манифестам}"

fail=0
for f in $(find "$target" -name '*.yaml' -o -name '*.yml'); do
  if grep -q "kind: Deployment" "$f" || grep -q "kind: StatefulSet" "$f"; then
    grep -q "resources:" "$f" || { echo "[!] $f: нет resources"; fail=1; }
    grep -q "readinessProbe:" "$f" || { echo "[!] $f: нет readinessProbe"; fail=1; }
    grep -q ":latest" "$f" && { echo "[!] $f: используется тег latest"; fail=1; }
  fi
done

exit $fail
