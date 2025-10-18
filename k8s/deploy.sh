kubectl apply -f ./namespace.yaml
kubectl apply -f ./secrets/secret.yaml
kubectl apply -f ./cluster-issuer.yaml



kubectl apply -f ./postgres/statefulset.yaml
kubectl apply -f ./postgres/service.yaml



# kubectl apply -f ./auth-service/configmap.yaml
kubectl apply -f ./auth-service/configmap-prod.yaml

kubectl apply -f ./auth-service/job.yaml
kubectl apply -f ./auth-service/deployment.yaml
kubectl apply -f ./auth-service/hpa.yaml

kubectl apply -f ./auth-service/service.yaml
kubectl apply -f ./auth-service/ingress.yaml
