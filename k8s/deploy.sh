#!/bin/bash

set -e  # Exit on any error

ENVIRONMENT=${1:-dev}
NAMESPACE="auth-service"

echo "Deploying to $ENVIRONMENT environment..."

# Install prerequisites if not exists
if ! kubectl get deployment cert-manager -n cert-manager &> /dev/null; then
    echo "Installing cert-manager..."
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
fi

# Apply namespace first
kubectl apply -f base/namespace.yaml

# Apply sealed secrets if using them
if [ -f "base/sealed-secret.yaml" ]; then
    kubectl apply -f base/sealed-secret.yaml
fi

# Deploy using kustomize
if [ "$ENVIRONMENT" = "dev" ]; then
    kubectl apply -k overlays/dev/
elif [ "$ENVIRONMENT" = "prod" ]; then
    kubectl apply -k overlays/prod/
else
    echo "Unknown environment: $ENVIRONMENT"
    exit 1
fi

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/postgres -n $NAMESPACE --timeout=300s
kubectl rollout status deployment/auth-service -n $NAMESPACE --timeout=300s

echo "Deployment completed successfully!"
echo "Resources in namespace $NAMESPACE:"
kubectl get all -n $NAMESPACE

echo "Ingress details:"
kubectl get ingress -n $NAMESPACE