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

## Helper scripts and deploy workflow

I added a small helper script to build, push and redeploy the backend image to your Kubernetes cluster.

Usage (from repo root):

```bash
# optional: set DOCKER_USER if you push to your own registry account
DOCKER_USER=connorwbrown ./deploy-backend.sh
```

What it does:
- builds the backend image using `Dockerfile.backend`
- tags it as `${DOCKER_USER}/flask-backend:latest` and pushes to Docker Hub
- updates the `backend` Deployment in the `cancelers-dilemma` namespace to use the new image and waits for the rollout

If you prefer to build locally into minikube's Docker daemon (no push), run:

```bash
eval $(minikube docker-env)
docker build -t flask-backend:latest -f Dockerfile.backend .
kubectl rollout restart deployment/backend -n cancelers-dilemma
kubectl rollout status deployment/backend -n cancelers-dilemma
```

## Frontend local env

There's a `frontend/.env.example` file showing how to set `REACT_APP_API_URL` for local development. Copy it to `frontend/.env.development` or set the env var in your shell before starting the dev server.


# Some Backlogged Feature Considerations:

TODO: 

UUIDs

p1.name, p2.name on creation page popup

Multiplayer

Setup with calendar event

Excuses:
https://www.fancycomponents.dev/docs/components/text/typewriter

Decision Selection:
https://css-irl.info/animating-underlines/


