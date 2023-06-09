######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

from typing import NamedTuple
from twingraph import component, pipeline


""" Note: In order to visualize using AWS Neptune workbench run the following:
    %%gremlin -p v,ine,outv,oute,inv,oute,inv
    g.V().inE().outV().outE().inV().outE().inV().path() """
    

@component(graph_config={'graph_endpoint':'wss://<AWS-DATABASE-ID>.<AWS-CLUSTER-ID>.<AWS-REGION-ID>.neptune.amazonaws.com:8182'})
def Func_A(inp_1: int, inp_2: float) -> NamedTuple:
    import numpy as np
    output_1 = np.multiply(inp_1, inp_2)
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)


@component(graph_config={'graph_endpoint':'wss://<AWS-DATABASE-ID>.<AWS-CLUSTER-ID>.<AWS-REGION-ID>.neptune.amazonaws.com:8182'})
def Func_B(inp_1: list, inp_2: float) -> NamedTuple:
    import numpy as np
    output_1 = np.multiply(np.average(inp_1), inp_2)
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)


@component(graph_config={'graph_endpoint':'wss://<AWS-DATABASE-ID>.<AWS-CLUSTER-ID>.<AWS-REGION-ID>.neptune.amazonaws.com:8182'})
def Func_C(inp_1: str, inp_2: float) -> NamedTuple:
    output_1 = str(inp_2)+inp_1
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)


@component(graph_config={'graph_endpoint':'wss://<AWS-DATABASE-ID>.<AWS-CLUSTER-ID>.<AWS-REGION-ID>.neptune.amazonaws.com:8182'})
def Func_D(inp_1: str, inp_2: float, inp_3: float, inp_4: float) -> NamedTuple:
    output_1 = str(inp_2+inp_3+inp_4)+inp_1
    from collections import namedtuple
    poutput = namedtuple('outputs', ['index', 'val'])
    return poutput(inp_1, output_1)


@pipeline(celery_pipeline=False, graph_config={'graph_endpoint':'wss://<AWS-DATABASE-ID>.<AWS-CLUSTER-ID>.<AWS-REGION-ID>.neptune.amazonaws.com:8182'})
def test_orchestration():
    i_1 = 5
    f_1 = 1.28

    g = Func_A(inp_1=i_1, inp_2=f_1)

    h = Func_B(parent_hash=[g['hash']], inp_1=[
                   i_1, g['outputs']['index'], g['outputs']['val']], inp_2=f_1)

    m = []
    for n in range(10):
        m.append(Func_C(parent_hash=[
                      g['hash'], h['hash']], inp_1='hello'+str(h['outputs']['index']), inp_2=g['outputs']['val']))
    
    q = []
    for j in range(5):
        q.append(Func_D(parent_hash=[
                      m[2*j]['hash'], g['hash'], h['hash']], inp_1=m[2*j]['outputs']['val'], inp_2 = i_1, inp_3 = g['outputs']['val'], inp_4 = h['outputs']['val']))
    


test_orchestration()
