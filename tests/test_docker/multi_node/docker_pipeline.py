######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

from twingraph import component, pipeline
from typing import NamedTuple
import numpy
import os 

docker_id = 'public.ecr.aws/docker/library/python:buster'

@component(docker_id=docker_id)
def Func_A_add(inp_1:float, inp_2:float) -> NamedTuple:
    output_1 = inp_1 + inp_2
    from collections import namedtuple
    poutput = namedtuple('outputs', ['output_1'])
    return poutput(output_1)

@component(docker_id=docker_id)
def Func_B_mult(directory:list, inp_1:float, inp_2:float) -> NamedTuple:
    output_2 = inp_1* inp_2
    from collections import namedtuple
    poutput = namedtuple('outputs', ['output_2'])
    return poutput(output_2)

@pipeline()
def pipeline_1():
    inputs = numpy.loadtxt('inputs_pipeline_1.csv')
    directory = os.getcwd()
    a = Func_A_add(inputs[0], inputs[1])
    b = Func_B_mult(directory, a['outputs']['output_1'], inputs[0], parent_hash=a['hash'])
    numpy.savetxt(directory+'/outputs_pipeline_1.csv', numpy.array([b['outputs']['output_2']]))
    
    
    
    

    
