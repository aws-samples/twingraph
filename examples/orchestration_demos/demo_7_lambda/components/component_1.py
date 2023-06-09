import json
from typing import NamedTuple
from twingraph import component

docker_id='<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/demo7:latest'
lambda_config=json.load(open("lambdaconfig.json", "r"))

@component(lambda_task=True, docker_id=docker_id, lambda_config=lambda_config)
def Func_C(inp_1: str, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2 += np.random.random()
    def getRow(rowIndex):
        """
        :type rowIndex: int
        :rtype: List[int]
        """
        last = [1]
        res = [1]
        for r in range(1, rowIndex + 1):
            res = [1]
            for index in range(len(last) - 1):
                res.append(last[index] + last[index + 1])
            res.append(1)
            last = res
        return res
    
    inp_2 += np.random.random()
    output_1 = str(inp_2) + inp_1
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_2, output_1)


@component(lambda_task=True, docker_id=docker_id, lambda_config=lambda_config)
def Func_D(inp_1: float, inp_2: float, inp_3: float, inp_4: float) -> NamedTuple:
    import numpy as np
    inp_2 += np.random.random()
    output_1 = str(inp_2 + inp_3 + inp_4) + str(inp_1)
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_2, output_1)
