######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

from twingraph import component, pipeline
from typing import NamedTuple
import numpy
import os 

@component()
def Func_A_add(directory:list, inp_1: float, inp_2: float) -> NamedTuple:
    import numpy as np
    output_1 = np.add(inp_1, inp_2)
    from collections import namedtuple
    poutput = namedtuple('outputs', ['output_1'])
    return poutput(output_1)

@component()
def Func_B_mult(directory:list, inp_1: float, inp_2: float) -> NamedTuple:
    import numpy as np
    output_1 = np.multiply(inp_1, inp_2)
    numpy.savetxt(directory+'/outputs_pipeline_1.csv',np.array([output_1]))
    from collections import namedtuple
    poutput = namedtuple('outputs', ['Dummy'])
    return poutput(None)

@pipeline()
def pipeline_1():
    inputs = numpy.loadtxt('inputs_pipeline_1.csv')
    directory = os.getcwd()
    a = Func_A_add(directory, inputs[0], inputs[1])
    b = Func_B_mult(directory, a['outputs']['output_1'], inputs[0], parent_hash=a['hash'])
    
    
    
    

    
