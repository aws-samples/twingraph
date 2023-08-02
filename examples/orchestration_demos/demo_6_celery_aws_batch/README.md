# Goal

Demonstrate how to create a set of tasks with dependencies that runs on a docker container using AWS Batch

Files

---

* components/component1.py: Defines a set of functions that works on the container demo2:latest
* components/component2.py: Defines a set of functions that works on the container demo2:latest
* attr.py: Meta data for the experiment/workflow
* batchconfig.json: Batch configuration to specify region and job queue name 
* deployment.py: Implementation of a selection of tasks to be run in the Docker container  

---

## Prerequisites  

1.    AWS CLI needs to be installed and configured (https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)
2.    AWS Batch environment, job queues and definitions need to be configured (https://docs.aws.amazon.com/batch/latest/userguide/what-is-batch.html)
3.    Ensure that you have successfully executed `demo_2` example and pushed the container from this example to your Elastic Container Registry (ECR) using `push_to_ecr.py`  

## How to run the example

Do the following in the order listed below

* Configure user 
```bash
aws configure
AWS Access Key ID: 
AWS Secret Access Key: 
Default region name: 
Default output format:
```

* Configure the batch queue
Modify the `batchconfig.json` to reflect your chosen region and queue name and other configurations
```json
{
    "region_name": "<AWS-REGION-ID>",
    "jobQueue": "twingraph-run-queue",
    "logGroupName": "/aws/batch/job",
    "vCPU": 1,
    "Mem": 2048
}

An AWS Batch queue/compute environment needs to be set up before this example can be executed
Remember to modify the `jobQueue` variable to your choice of the AWS Batch queue name.  

```
Run the orchestration pipeline
```bash
python deployment.py 
```


 
If your tasks fail to launch on AWS Batch, ensure your Region ID and Job Queue Names are correct.  Additionally ensure that AWS Batch is able to run the `getting-started-wizard-job`.  If you are new to AWS Batch, we recommend that you use the wizard (https://<AWS-REGION-ID>.console.aws.amazon.com/batch/home?region=<AWS-REGION-ID>#wizard) to setup your AWS Batch environnement.  If your task fails to run on AWS Batch, you need clear your local celery task runners before attempting to launch a new AWS Batch job. This can be achieved by running the script as shown below 

Change directory to the utilities to clean up:
```
cd {YOUR DIRECTORY FOR TwinGraph}/examples/utils
python stop_and_delete.py
```

