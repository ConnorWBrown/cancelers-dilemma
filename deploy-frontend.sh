#!/usr/bin/env bash
set -euo pipefail

# Usage:
# DOCKER_USER=yourdockerid ./deploy-frontend.sh
# If DOCKER_USER is not set, it defaults to 'connorwbrown'.

DOCKER_USER=${DOCKER_USER:-connorwbrown}
IMAGE_NAME="${DOCKER_USER}/react-frontend:latest"
NAMESPACE=${NAMESPACE:-cancelers-dilemma}

echo "Building frontend image (local tag: react-frontend:latest)..."
# docker build -t react-frontend:latest -f Dockerfile.frontend ./frontend || docker build -t react-frontend:latest -f Dockerfile.frontend .
docker build -t react-frontend:latest -f Dockerfile.frontend .
echo "Tagging image -> ${IMAGE_NAME}"
docker tag react-frontend:latest "${IMAGE_NAME}"

echo "Pushing ${IMAGE_NAME} to registry..."
docker push "${IMAGE_NAME}"

echo "Updating k8s deployment 'frontend' in namespace ${NAMESPACE} to use ${IMAGE_NAME}"
kubectl set image deployment/frontend react-frontend="${IMAGE_NAME}" -n "${NAMESPACE}" || {
  echo "kubectl set image failed, attempting rollout restart"
  kubectl rollout restart deployment/frontend -n "${NAMESPACE}"
}

echo "Waiting for rollout to finish..."
kubectl rollout status deployment/frontend -n "${NAMESPACE}"

echo "Frontend redeployed successfully."
