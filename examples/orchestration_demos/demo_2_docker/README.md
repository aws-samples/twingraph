# Goal

Demonstrate how to create a docker container, operate on that container by using a collection of tasks and then finally push the container to ECR 

Files

---

* Dockerfile: Dockerfile to describe what should be in the container  
* build_tag_docker.py: Builds a Docker image based on the Dockerfile  
* deployment.py: Implementation with a selection of tasks to be run in the Docker container  
* push_to_ecr.py: Push the created Docker image to ECR repository  

---

## Prerequisites  

1. Try Demo 1 and familiarize with the control flow, components and pipelines.
2. Ensure that Docker is running with:
```bash
docker info
```
3.    AWS CLI needs to be installed and configured (https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)
4.    Elastic Container Registry needs to be setup (https://docs.aws.amazon.com/AmazonECR/latest/userguide/get-set-up-for-amazon-ecr.html)

## How to run the example

Do the following in the order listed below

Read the Dockerfile, add any packages you wish to install.

Build the docker image
```bash
python build_tag_docker.py 
```
Run the orchestration pipeline
```bash
python deployment.py 
```
Configure aws-cli in order to push the container to ECR (this step is not required to actually run the deployment script)
```bash
aws configure
AWS Access Key ID: 
AWS Secret Access Key: 
Default region name: 
Default output format: 
```

Push the docker image to ECR, because this will be needed in the following demos 
```bash
python push_to_ecr.py 
```
## Understanding the Python Code

This code is identical to the previous demo, with the notable exception that some of the decorators have the docker image id embedded, for example:

```python
@component(docker_id=docker_id, additional_attributes=additional_attributes)
def Func_A(input_1: float, input_2: float) -> NamedTuple:
    from collections import namedtuple
    outputs_namedtuple = namedtuple('outputs', ['sum'])
    return outputs_namedtuple(input_1 + input_2)
```

Additionally, further static attributes are added to each node in the graph as implied by the additional_attributes variable.