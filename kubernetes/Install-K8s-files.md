# Deploy the model
kubectl apply -f deployment.yaml

# Expose the service
kubectl apply -f service.yaml

# apply horizontal POD autoscaling
kubectl apply -f hpa.yaml

# port forward the service port 80 to localhost:8000
kubectl port-forward service/breast-cancer-classifier-service 8000:80 --address 0.0.0.0 &

# curl the service
curl http://localhost:8000/health

# Identify the label of the node you want to schedule the deployment on 
kubectl get nodes --show-labels

# Apply node affinity
kubectl patch deployment breast-cancer-classifier-deployment -p '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/hostname":"node01"}}}}}'

# Check affinity configuration 
kubectl describe deployment breast-cancer-classifier-deployment