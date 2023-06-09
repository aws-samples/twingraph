######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

from twingraph import component, pipeline
from typing import NamedTuple
import numpy
import os 

@component()
def Func_A_mult(directory:list, inp_1: int, inp_2: float) -> NamedTuple:
    import numpy as np
    output_1 = np.multiply(inp_1, inp_2)
    numpy.savetxt(directory+'/outputs_pipeline_1.csv',np.array([output_1]))
    print(directory+'outputs_pipeline_1.csv',np.array([output_1]))
    from collections import namedtuple
    poutput = namedtuple('outputs', ['Dummy'])
    return poutput(None)


@pipeline()
def pipeline_1():
    inputs = numpy.loadtxt('inputs_pipeline_1.csv')
    Func_A_mult(os.getcwd(), int(inputs[0]), inputs[1])
    

    
