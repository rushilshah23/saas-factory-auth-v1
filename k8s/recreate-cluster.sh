kind delete cluster --name cluster-1

kind create cluster --config ./kind-cluster-template-1.yaml --name cluster-1

# Apply ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml


# Metrics
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml


# Sealed secrets
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.26.0/controller.yaml


# Certificate manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# # VPA
# kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vpa-release-1.32.0/vpa-crd.yaml
# kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vpa-release-1.32.0/vpa-rbac.yaml
# kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vpa-release-1.32.0/vpa-deployment.yaml


# # Load images from host machine to kind
# kind load docker-image todo-frontend-react:latest todo-backend:latest  --name cluster-1