#!/usr/bin/env bash
# Bring the full Argus stack up on a local kind cluster from locally built images.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

CLUSTER="${KIND_CLUSTER:-argus}"
NAMESPACE="${ARGUS_NAMESPACE:-argus}"

for tool in docker kind kubectl helm; do
  command -v "$tool" >/dev/null 2>&1 || { echo "missing required tool: $tool"; exit 1; }
done

if ! kind get clusters | grep -qx "$CLUSTER"; then
  echo "Creating kind cluster '$CLUSTER'..."
  kind create cluster --name "$CLUSTER" --config deploy/k8s/kind-cluster.yaml
fi

echo "Building images..."
docker build -t argus-gateway:local -f services/gateway/Dockerfile .
docker build -t argus-web:local web

echo "Loading images into kind..."
kind load docker-image argus-gateway:local --name "$CLUSTER"
kind load docker-image argus-web:local --name "$CLUSTER"

echo "Deploying with Helm..."
helm upgrade --install argus deploy/helm/argus \
  --namespace "$NAMESPACE" --create-namespace \
  --set anthropicApiKey="${ANTHROPIC_API_KEY:-}"

kubectl -n "$NAMESPACE" rollout status deploy/gateway --timeout=180s
kubectl -n "$NAMESPACE" rollout status deploy/web --timeout=180s

echo
echo "Argus is up. Open http://localhost:8080"
