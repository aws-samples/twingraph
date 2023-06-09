
# Manual Full Installation Steps & Using Poetry Env or Pip Wheel

* Note: The instructions below work for AL2, Centos, Fedora & RHEL; swap the package manager from *yum* to *apt* for Ubuntu and Debian systems

Install [Python](https://wiki.python.org/moin/BeginnersGuide/Download), and install [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (or Miniconda) for managing Python environments.

Install [Docker](https://docs.docker.com/get-docker/) & make sure service is running:
```bash
sudo usermod -aG docker $USER
sudo systemctl start docker
```

Install Redis, and ensure it is running. If using Amazon Linux 2 on AWS, you can use the following:
```bash
sudo amazon-linux-extras install redis6
sudo systemctl enable redis
sudo systemctl start redis
redis-cli ping
```
Otherwise you can obtain it per the following instructions here: https://redis.io/docs/getting-started/installation/install-redis-on-linux/

Get RabbitMQ docker image, and have that running.
```bash
docker run -d -p 5672:5672 rabbitmq
```
Installing AWS Command Line Interface (AWS CLI)

AWS Command Line Interface is an open source tool that enables you to interact with AWS services using a command line interface.  More information can be found here (https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)  
If AWS CLI is installed successfully, you should see something similar to the following
```bash
$ aws --version
aws-cli/2.10.0 Python/3.11.2 Linux/4.14.133-113.105.amzn2.x86_64 botocore/1.13
```

Git-LFS
Set up the environment to install Git LFS.
Instructions below are given for Amazon Linux 2:

Obtain Tinkerpop (Gremlin graph database) through docker and have that running.
```bash
docker run -d -p 8182:8182 tinkerpop/gremlin-server:3.6.1
```

Clone the code 
```bash
git clone https://github.com/aws-samples/twingraph.git
```

Local Git to retrieve the latest meta-data and copy the changes from the remote repository
```bash
git lfs fetch --all
git lfs pull
```

Obtain Gremlin visualizer through docker and have that running.
```bash
docker run --rm -d --net=host --name=gremlin-visualizer prabushitha/gremlin-visualizer:latest
```
In order to use this, port forward 3000 and 3001 to your local host.  

Optional: If using Kubernetes (MiniKube, EKS, etc.) set up Kubectl (https://kubernetes.io/docs/tasks/tools/) with dashboard:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl proxy
```

Change into folder and install all required packages using the following commands:
```bash
poetry build
pip install dist/twingraph-*.whl
```

Alternatively, use poetry to make a new environment:
```bash
poetry install
poetry shell
```

(**OPTIONAL**) : In order to visualize celery task status, you can run celery flower on the backend (with RabbitMQ) within the poetry-generated virtual python environment:
```bash
(twingraph-env) celery flower
```

(**OPTIONAL**) : If using Redis backend you need to modify the celery flower invocation:
```bash
(twingraph-env) celery --broker=redis://localhost:6379/1 flower
```
