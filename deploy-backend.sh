#!/usr/bin/env bash
set -euo pipefail

# Usage:
# DOCKER_USER=yourdockerid ./deploy-backend.sh
# If DOCKER_USER is not set, it defaults to 'connorwbrown'.

DOCKER_USER=${DOCKER_USER:-connorwbrown}
IMAGE_NAME="${DOCKER_USER}/flask-backend:latest"
NAMESPACE=${NAMESPACE:-cancelers-dilemma}

echo "Building backend image (local tag: flask-backend:latest)..."
docker build -t flask-backend:latest -f Dockerfile.backend .

echo "Tagging image -> ${IMAGE_NAME}"
docker tag flask-backend:latest "${IMAGE_NAME}"

echo "Pushing ${IMAGE_NAME} to registry..."
docker push "${IMAGE_NAME}"

echo "Updating k8s deployment 'backend' in namespace ${NAMESPACE} to use ${IMAGE_NAME}"
kubectl set image deployment/backend flask-backend="${IMAGE_NAME}" -n "${NAMESPACE}" || {
  echo "kubectl set image failed, attempting rollout restart"
  kubectl rollout restart deployment/backend -n "${NAMESPACE}"
}

echo "Waiting for rollout to finish..."
kubectl rollout status deployment/backend -n "${NAMESPACE}"

echo "Backend redeployed successfully."
