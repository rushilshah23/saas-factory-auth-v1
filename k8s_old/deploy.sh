#!/bin/bash

set -e  # Exit on any error

ENVIRONMENT=${1:-dev}
NAMESPACE="auth-service"

echo "Deploying to $ENVIRONMENT environment..."

# Create namespace first
kubectl apply -f base/namespace.yaml

# Apply sealed secrets first (if they exist)
if [ -f "sealed-secrets/sealed-secret.yaml" ]; then
    echo "Applying sealed secrets..."
    kubectl apply -k sealed-secrets/
    
    # Wait for secrets to be available
    echo "Waiting for secrets to be ready..."
    sleep 10
fi

# Deploy using kustomize for the specific environment
if [ "$ENVIRONMENT" = "dev" ]; then
    echo "Applying dev configuration..."
    kubectl apply -k overlays/dev/
elif [ "$ENVIRONMENT" = "prod" ]; then
    echo "Applying prod configuration..."
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