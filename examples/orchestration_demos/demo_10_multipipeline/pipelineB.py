######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################


from typing import NamedTuple
from twingraph import component, pipeline
import json


@component(docker_id='demo1:latest')
def Func_A(inp_1: int, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2+=np.random.random()
    output_1 = np.multiply(inp_1, inp_2)
    from collections import namedtuple
    poutput = namedtuple("outputs", ['index', 'val', 'val2', 'val3'])
    return poutput(inp_1, output_1, [output_1+np.random.random() for k in range(25)], [output_1+np.random.random() for k in range(3)])


@component(docker_id='demo1:latest')
def Func_B(inp_1: list, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2+=np.random.random()
    output_1 = np.multiply(np.average(inp_1), inp_2)
    from collections import namedtuple
    poutput = namedtuple("outputs", ['index', 'val'])
    return poutput(inp_1, output_1)


@component(docker_id='demo1:latest')
def Func_C(inp_1: str, inp_2: float) -> NamedTuple:
    import numpy as np
    inp_2+=np.random.random()
    inp_2+=np.random.random()
    output_1 = str(inp_2) + inp_1
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)


@component(docker_id='demo1:latest')
def Func_D(inp_1: str, inp_2: float, inp_3: float, inp_4: float) -> NamedTuple:
    import numpy as np
    inp_2+=np.random.random()
    output_1 = str(inp_2 + inp_3 + inp_4) + inp_1
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)


@pipeline(celery_pipeline=True, celery_include_files=[], clear_graph=False, multipipeline=True)
def test_orchestration_B():
    i_1 = 5
    f_1 = 1.28

    g = Func_A(inp_1=i_1, inp_2=f_1)

    h = Func_B(parent_hash=[g['hash']], inp_1=[
                   i_1, g['outputs']['index'], g['outputs']['val']], inp_2=f_1)

    m = []
    for n in range(20):
        m.append(Func_C(parent_hash=[
            g['hash'], h['hash']], inp_1='hello' + str(h['outputs']['index']), inp_2=g['outputs']['val']))

    q = []
    for j in range(10):
        q.append(Func_D(parent_hash=[
            m[2 * j]['hash'], g['hash'], h['hash']], inp_1=m[2 * j]['outputs']['val'], inp_2=i_1, inp_3=g['outputs']['val'], inp_4=h['outputs']['val']))


test_orchestration_B()
