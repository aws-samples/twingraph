import json
from typing import NamedTuple
from twingraph import component

# 
@component(kubernetes_task=True, docker_id='<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/demo1:latest', additional_attributes=json.load(open("attr.json", "r")))
def Func_A(inp_1: int, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2 += np.random.random()
    output_1 = np.multiply(inp_1, inp_2)

    from collections import namedtuple
    poutput = namedtuple("outputs", ['index', 'val', 'val2', 'val3'])
    return poutput(inp_1, output_1, [output_1 + np.random.random() for k in range(int(2e2))], [output_1 + np.random.random() for k in range(3)])


@component(kubernetes_task=True, docker_id='<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/demo1:latest', additional_attributes=json.load(open("attr.json", "r")))
def Func_B(inp_1: list, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2 += np.random.random()
    output_1 = np.multiply(np.average(inp_1), inp_2)
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)
