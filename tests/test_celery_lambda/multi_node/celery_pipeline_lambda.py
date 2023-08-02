######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

from twingraph import component, pipeline
from typing import NamedTuple

docker_id = '<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/demo7:latest'
lambda_config = {
    "iam_role": "arn:aws:iam::<AWS-ACCOUNT-ID>:role/<LAMBDA-CLOUDWATCH-ROLE>",
    "architecture": "x86_64",
    "storage_size": 512,
    "memory_size": 512,
    "region_name": "<AWS-REGION-ID>",
    "timeout": 900
}
@component(lambda_task=True, lambda_config=lambda_config, docker_id=docker_id)
def Func_A_add(inp_1:float, inp_2:float) -> NamedTuple:
    output_1 = inp_1 + inp_2
    from collections import namedtuple
    poutput = namedtuple('outputs', ['output_1'])
    return poutput(output_1)

@component(lambda_task=True, lambda_config=lambda_config, docker_id=docker_id)
def Func_B_mult(inp_1:float, inp_2:float) -> NamedTuple:
    output_2 = inp_1*inp_2
    from collections import namedtuple
    poutput = namedtuple('outputs', ['output_2'])
    return poutput(output_2)

@pipeline(lambda_pipeline=True, celery_pipeline=True, redirect_logging=False)
def pipeline_celery_lambda():
    import numpy
    inputs = numpy.loadtxt('inputs_pipeline_celery_lambda.csv')
    a = Func_A_add(inputs[0], inputs[1])
    b = Func_B_mult(inputs[0], a['outputs']['output_1'], parent_hash=a['hash'])
    numpy.savetxt('outputs_pipeline_celery_lambda.csv', numpy.array([b['outputs']['output_2']]))
    
pipeline_celery_lambda()

    
    
    
    

    
