# Goal

Demonstrate how to create a set of tasks with dependencies that runs on a docker container using Kubernetes in (1) Minikube and (2) EKS.

Files

---

* components/component1.py: Defines a set of functions that works on the container demo1:latest
* components/component2.py: Defines a set of functions that works on the container demo1:latest
* attr.py: Meta data for the experiment/workflow
* eks-blueprint-twingraph.yaml: k8s manifest to be used for option 2 deployment in AWS EKS
* deployment.py: Implementation of a selection of tasks to be run in the Docker container  

---

## Prerequisites  

1.    AWS CLI needs to be installed and configured (https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)
2.    Kubernetes has to installed either using Minikube (https://minikube.sigs.k8s.io/docs/start/) if you intend to run locally, or AWS EKS Blueprint (https://aws-quickstart.github.io/cdk-eks-blueprints/) to run on AWS EKS
3.    Ensure that you have successfully executed `demo_1` example and pushed the container from this example to your Elastic Container Registry (ECR) using `push_to_ecr.py`  

## Option 1: Run k8s locally using Minikube 
Install and start Minikube with the steps below to be able to run the demo example in k8s locally

Install the latest minikube stable release using binary download
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

Start you cluster
```bash
minikube start
```

Install `kubectl` to check the status of your cluster from the terminal
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

For additional insight into your cluster state, use Minikube Dashboard
```bash
minikube dashboard
```
Use the link provided after the dashboard launches

Configure the registry credentials to be used by Minikube so it finds the image you pushed to AWS ECR when running demo_1
```bash
minikube addons configure registry-creds

Do you want to enable AWS Elastic Container Registry? [y/n]: y
-- Enter AWS Access Key ID: 
-- Enter AWS Secret Access Key: 
-- (Optional) Enter AWS Session Token: 
-- Enter AWS Region: 
-- Enter 12 digit AWS Account ID (Comma separated list): 
-- (Optional) Enter ARN of AWS role to assume: 

Do you want to enable Google Container Registry? [y/n]: n

Do you want to enable Docker Registry? [y/n]: n

Do you want to enable Azure Container Registry? [y/n]: n
```
Enable the registry addon 
```bash
minikube addons enable registry-creds
```

## Option 2: Run k8s using AWS EKS - Easy Install
Fill in the following information in per needs (remove the <>).
```bash
export CLUSTER_NAME=<NAME-OF-CLUSTER>
export CLUSTER_REGION=<AWS-REGION-ID>
export INSTANCE_TYPES=<INSTANCE-TYPE>
```
Create a cluster with the following:
```bash
eksctl create cluster --name ${CLUSTER_NAME} --version 1.22 --region ${CLUSTER_REGION} --nodegroup-name linux-nodes --node-type ${} --nodes 2 --nodes-min 2 --nodes-max 10 --managed --with-oidc --auto-kubeconfig
```
Once created, run the following:
```bash
aws eks --region ${CLUSTER_REGION} update-kubeconfig --name ${CLUSTER_NAME}
```

## Option 3: Run k8s using AWS EKS - EKS Blueprints
Use the AWS EKS blueprint to deploy an EKS cluster

Install the packages Node.js, npm and cdk required by the module eks-blueprints
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
. ~/.nvm/nvm.sh
nvm install 16
node -e "console.log('Running Node.js ' + process.version)"
npm install -g aws-cdk
```

Create a directory that represents you project (e.g. eks-blueprints) and then create a new typescript CDK project in that directory
```bash
mkdir eks-blueprints
cd eks-blueprints
cdk init app --language typescript
```

Install the eks-blueprints NPM package
```bash
npm i @aws-quickstart/eks-blueprints
```

Replace the contents of <eks-blueprints>/bin/<your-main-file>.ts with the following
```bash
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';

const app = new cdk.App();
const account = <AWS-ACCOUNT-ID>;
const region = '<AWS-REGION-ID>';

const addOns: Array<blueprints.ClusterAddOn> = [
    new blueprints.addons.ArgoCDAddOn(),
    new blueprints.addons.CalicoOperatorAddOn(),
    new blueprints.addons.MetricsServerAddOn(),
    new blueprints.addons.ClusterAutoScalerAddOn(),
    new blueprints.addons.AwsLoadBalancerControllerAddOn(),
    new blueprints.addons.VpcCniAddOn(),
    new blueprints.addons.CoreDnsAddOn(),
    new blueprints.addons.KubeProxyAddOn(),
    new blueprints.addons.EfsCsiDriverAddOn()
];

const blueprint = blueprints.EksBlueprint.builder()
    .account(account)
    .region(region)
    .addOns(...addOns) 
    .useDefaultSecretEncryption(true) // set to false to turn secret encryption off (non-production/demo cases)
    .build(app, 'eks-blueprint-twingraph');
```

Bootstrap your environment 
```bash
cdk bootstrap
```

Deploy the stack using (this will roughly take 20mins)
```bash
cdk deploy
```

Install `kubectl` to interact with your cluster
```bash
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.23.6/bin/linux/amd64/kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

Identify the IAM role used to create the cluster by searching for the CreateCluster API call in AWS CloudTrail, and then take note of the userIdentity section of the API call.

Update `kubeconfig` with your AWS EKS cluster details
```bash
rm ~/.kube/config
aws eks update-kubeconfig --name eks-blueprint-twingraph --role-arn arn:aws:iam::<user-id>:role/<eks-cluster-creator-role>
```

Test your configuration
```bash
kubectl get svc
```

Create a namespace and apply the deployment manifest to your cluster
```bash
kubectl create namespace eks-blueprint-twingraph
kubectl apply -f eks-blueprint-twingraph.yaml
```

View all resources that exist in the namespace
```bash
kubectl get all -n eks-blueprint-twingraph
```

## How to run the example

Do the following in the order listed below

Configure user 
```bash
aws configure
AWS Access Key ID: 
AWS Secret Access Key: 
Default region name: 
Default output format: 
```

Update the demo files with your AWS credentials
```bash
cd examples/utils
python update_credentials.py
```

Run the orchestration pipeline
```bash
python deployment.py 
```

If you wish to interrupt or stop Celery, change directory to the utilities directory and run the provided script.
```
cd {YOUR DIRECTORY FOR TwinGraph}/examples/utils
python stop_and_delete.py
```

