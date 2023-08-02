######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

from twingraph import component, pipeline
import json 
from typing import NamedTuple

ecr_docker_id_1 = '<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/demo2:latest'
ecr_docker_id_7 = '<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/demo7:latest'
standard_attributes = json.load(open("attr.json", "r"))
lambda_config=json.load(open("lambdaconfig.json", "r"))
batch_config=json.load(open("batchconfig.json", "r"))

# Func A is running locally on Docker Compose
@component(docker_id=ecr_docker_id_1, additional_attributes=standard_attributes)
def Func_A(inp_1: int, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2 += np.random.random()
    
    # random permutation operation 
    def permute(nums):
        # DPS with swapping
        res = []
        if len(nums) == 0:
            return res
        get_permute(res, nums, 0)
        return res

    def get_permute(res, nums, index):
        if index == len(nums):
            res.append(list(nums))
            return
        for i in range(index, len(nums)):
            nums[i], nums[index] = nums[index], nums[i]
            # s(n) = 1 + s(n-1)
            get_permute(res, nums, index + 1)
            nums[i], nums[index] = nums[index], nums[i]

    output_1 = np.sum(np.array(permute([inp_1, inp_2])))
    from collections import namedtuple
    poutput = namedtuple("outputs", ['index', 'val', 'val2', 'val3'])
    return poutput(inp_1, output_1, [output_1 + np.random.random() for k in range(int(3))], [output_1 + np.random.random() for k in range(3)])

# Func B is running on AWS Lambda
@component(lambda_task=True, docker_id=ecr_docker_id_7, lambda_config=lambda_config, additional_attributes=standard_attributes)
def Func_B(inp_1: list, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2 += np.random.random()
    def mySqrt(x):
        # sqrt(x) = 2 * sqrt(x / 4) for n % 4 == 0
        # sqrt(x) = 1 + 2 * sqrt(x / 4) for n % 4 != 0
        if x == 0:
            return 0
        if x < 4:
            return 1
        res = 2 * mySqrt(x / 4)
        # (res + 1) * (res + 1) >= 0 for avoiding overflow
        if (res + 1) * (res + 1) <= x and (res + 1) * (res + 1) >= 0:
            return res + 1
        return  res
    
    output_1 = mySqrt(np.multiply(np.average(inp_1), inp_2))
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)

# Func C is running on Amazon EKS
@component(kubernetes_task=True, docker_id=ecr_docker_id_1, additional_attributes=standard_attributes)
def Func_C(inp_1: str, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2 += np.random.random()
    output_1 = str(inp_2) + inp_1
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_2, output_1)

# Func D is running on AWS Batch
@component(batch_task=True, docker_id=ecr_docker_id_1, batch_config=batch_config, additional_attributes=standard_attributes)
def Func_D(inp_1: float, inp_2: float, inp_3: float, inp_4: float) -> NamedTuple:
    import numpy as np
    import random
    inp_2 += np.random.random()
    # concatenate some strings
    output_1 = str(inp_2 + inp_3 + inp_4) + str(inp_1)
     
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val', 'random_value'])
    return poutput(inp_2, output_1, random.random())

# Func E is running locally (no Docker) - simple passthrough function
@component()
def Func_E(inp_1: float) -> NamedTuple:
    from collections import namedtuple
    poutput = namedtuple('outputs', ['random_value'])
    return poutput(inp_1)


# Dynamic Pipeline
@pipeline(lambda_pipeline=True, batch_pipeline=True, kubernetes_pipeline=True, celery_pipeline=True, celery_concurrency_threads=16, redirect_logging=True)
def test_orc():
    import random 
    
    i_1 = 5
    f_1 = 1.28

    g = Func_A(inp_1=i_1, inp_2=f_1)

    h = Func_B(parent_hash=[g['hash']], inp_1=[
                   i_1, g['outputs']['index'], g['outputs']['val']], inp_2=f_1)

    m = []
    for n in range(random.randint(16,32)):
        m.append(Func_C(parent_hash=[
            g['hash'], h['hash']], inp_1='hello' + str(h['outputs']['index']), inp_2=g['outputs']['val']))

    q = []
    for j in range(random.randint(4,8)):
        q.append(Func_D(parent_hash=[
            m[2 * j]['hash'], g['hash'], h['hash']], inp_1=m[2 * j]['outputs']['index'], inp_2=i_1, inp_3=g['outputs']['val'], inp_4=h['outputs']['val']))

    for q_d in q:
        e = Func_E(parent_hash = q_d['hash'], inp_1=q_d['outputs']['random_value'])
        for k in range(random.randint(0,3)):
            e_i = e
            for i in range(2):
                e = Func_E(parent_hash = e_i['hash'], inp_1=e_i['outputs']['random_value'])

test_orc()
