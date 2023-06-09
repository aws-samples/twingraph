######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

from twingraph import component, pipeline
from typing import NamedTuple
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

@component()
def Func_A_add(inp_1:float, inp_2:float) -> NamedTuple:
    output_1 = inp_1 + inp_2
    from collections import namedtuple
    poutput = namedtuple('outputs', ['output_1'])
    return poutput(output_1)

@component()
def Func_B_mult(inp_1:float, inp_2:float) -> NamedTuple:
    output_2 = inp_1*inp_2
    from collections import namedtuple
    poutput = namedtuple('outputs', ['output_2'])
    return poutput(output_2)

@pipeline(celery_pipeline=True, redirect_logging=False)
def pipeline_celery_local():
    import numpy
    inputs = numpy.loadtxt('inputs_pipeline_celery_local.csv')
    a = Func_A_add(inputs[0], inputs[1])
    b = Func_B_mult(inputs[0], a['outputs']['output_1'], parent_hash=a['hash'])
    numpy.savetxt('outputs_pipeline_celery_local.csv', numpy.array([b['outputs']['output_2']]))

    
pipeline_celery_local()
    
    

    
