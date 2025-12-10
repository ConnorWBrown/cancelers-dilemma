# Canceler's Dilemma
Want to cancel on plans, but I-don't-want-to-if-you-don't-want-to? Quite the prisoner's dilemma. How about if we both want to cancel, we both click here?

Local Minikube Deployment:

'''

minikube start

eval $(minikube docker-env)

#next two might be overlapped

docker build -t flask-backend:latest -f Dockerfile.backend .
docker build -t react-frontend:latest -f Dockerfile.frontend .

<!-- docker build -t flask-backend:latest .                             -->
<!-- docker tag flask-backend:latest docker.io/library/flask-backend:latest
docker push docker.io/library/flask-backend:latest -->

docker tag flask-backend:latest connorwbrown/flask-backend:latest && docker push connorwbrown/flask-backend:latest

docker tag react-frontend:latest connorwbrown/react-frontend:latest && docker push connorwbrown/react-frontend:latest

kubectl apply -f k8s/backend-deployment.yml

kubectl apply -f k8s/frontend-deployment.yml

'''

minikube service -n cancelers-dilemma frontend --url
# ^^^ gives the address I can access the FE from, and the 


Local:

node run build

# Some Backlogged Feature Considerations:

TODO: 

UUIDs

Multiplayer

Setup with calendar event

Excuses:
https://www.fancycomponents.dev/docs/components/text/typewriter

Decision Selection:
https://css-irl.info/animating-underlines/


