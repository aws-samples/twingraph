import json
from typing import NamedTuple
from twingraph import component

docker_id='<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/demo1:latest'
batch_config=json.load(open("batchconfig.json", "r"))
additional_attributes=json.load(open("attr.json", "r"))

@component(batch_task=True, docker_id=docker_id, batch_config=batch_config, additional_attributes=additional_attributes)
def Func_C(inp_1: str, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2 += np.random.random()
    output_1 = str(inp_2) + inp_1
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)


@component(batch_task=True, docker_id=docker_id, batch_config=batch_config, additional_attributes=additional_attributes)
def Func_D(inp_1: str, inp_2: float, inp_3: float, inp_4: float) -> NamedTuple:
    import numpy as np
    inp_2 += np.random.random()
    output_1 = str(inp_2 + inp_3 + inp_4) + inp_1
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)
