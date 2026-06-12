#!/usr/bin/env bash
# Tear down the local kind cluster.
set -euo pipefail

CLUSTER="${KIND_CLUSTER:-argus}"

if kind get clusters | grep -qx "$CLUSTER"; then
  kind delete cluster --name "$CLUSTER"
else
  echo "kind cluster '$CLUSTER' not found"
fi
