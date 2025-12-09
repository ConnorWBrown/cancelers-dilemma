docker build -t flask-backend:latest -f Dockerfile.backend .
docker build -t react-frontend:latest -f Dockerfile.frontend .

docker tag flask-backend:latest connorwbrown/flask-backend:latest && docker push connorwbrown/flask-backend:latest

docker tag react-frontend:latest connorwbrown/react-frontend:latest && docker push connorwbrown/react-frontend:latest

kubectl apply -f k8s/backend-deployment.yml

kubectl apply -f k8s/frontend-deployment.yml

