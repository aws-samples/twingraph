import json
from typing import NamedTuple
from twingraph import component

@component(lambda_task=True, docker_id='<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/demo7:latest', lambda_config=json.load(open("lambdaconfig.json", "r")))
def Func_A(inp_1: int, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2 += np.random.random()
    output_1 = np.multiply(inp_1, inp_2)
    
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
            
    from collections import namedtuple
    poutput = namedtuple("outputs", ['index', 'val', 'val2', 'val3'])

    return poutput(inp_1, output_1, [output_1 + np.random.random() for k in range(int(2e1))], [output_1 + np.random.random() for k in range(3)])


@component(lambda_task=True, docker_id='<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/demo7:latest', lambda_config=json.load(open("lambdaconfig.json", "r")))
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
    
    output_1 = np.multiply(np.average(inp_1), inp_2)
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)
