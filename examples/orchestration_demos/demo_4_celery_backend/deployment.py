######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

# Begin by importing the type NamedTuple, which we exclusively use as a medium for all data transfers between components
from typing import NamedTuple
from twingraph import component, pipeline
import json

docker_id = 'demo1:latest'
additional_attributes = json.load(open("attr.json", "r"))

@component(docker_id=docker_id, additional_attributes=additional_attributes)
def Func_A(input_1: float, input_2: float) -> NamedTuple:
    from collections import namedtuple
    outputs_namedtuple = namedtuple('outputs', ['sum'])
    return outputs_namedtuple(input_1 + input_2)

@component(docker_id=docker_id, additional_attributes=additional_attributes)
def Func_B_multiply(input_1: float, input_2: float) -> NamedTuple:
    import numpy as np
    output_1 = np.multiply(input_1, input_2)
    from collections import namedtuple
    outputs = namedtuple('outputs', ['multiplication'])
    return outputs(output_1)

@component(docker_id=docker_id)
def Func_C_subtract(input_1, input_2):
    from collections import namedtuple
    outputs = namedtuple('outputs', ['subtraction'])
    return outputs(input_1 - input_2)

@component()
def Func_D_divide(input_1, input_2) -> NamedTuple:
    import numpy as np
    division = input_1 / input_2
    random_sign = np.random.random()-0.5
    from collections import namedtuple
    outputs = namedtuple('outputs', ['division'])
    return outputs(division * random_sign)


@component(docker_id=docker_id)
def Func_E_average(input_1, input_2, input_3, input_4) -> NamedTuple:
    import numpy as np
    output_1 = np.mean([input_1, input_2, input_3, input_4])
    from collections import namedtuple
    outputs = namedtuple('outputs', ['average'])
    return outputs(output_1)

# Finally, define a pipeline which strings together individual functions - Note that we have included Celery here
@pipeline(celery_concurrency_threads=32, celery_pipeline=True, celery_include_files=[])
def test_orchestration():
    import random
    # Begin by defining input values, e.g. floats
    float_number_1 = 3.14159
    float_number_2 = 1

    func_A = Func_A(float_number_2, input_1=float_number_1)

    func_B = Func_B_multiply(
        float_number_1, func_A['outputs']['sum'], parent_hash=func_A['hash'])

    func_C_collection = []
    for n in range(20):
        parent_hash = [func_A['hash'], func_B['hash']]
        func_C_collection.append(Func_C_subtract(
            parent_hash=parent_hash, input_1=func_A['outputs']['sum'], input_2=func_B['outputs']['multiplication']))

    func_D_collection = []
    for j in range(random.randint(0, 9)):
        parent_hash = [func_A['hash'], func_C_collection[2 * j]['hash']]
        func_D_collection.append(Func_D_divide(
            func_C_collection[2 * j]['outputs']['subtraction'], func_A['outputs']['sum'], parent_hash=parent_hash))
        
    # We can set control flow based on intermediate outputs also in a runtime dynamic manner
    func_E_collection = []
    for func_C in func_C_collection:
        for func_D in func_D_collection:
            if random.randint(0,9) < 2:
                # Only add Es if the parent function D is positive (remember that it is set randomly at runtime)
                if func_D['outputs']['division'] >= 0:
                    parent_hash = [func_A['hash'], func_B['hash'],
                                func_C['hash'], func_D['hash']]
                    func_E_collection.append(Func_E_average(func_A['outputs']['sum'], func_B['outputs']['multiplication'],
                                            func_C['outputs']['subtraction'], func_D['outputs']['division'], parent_hash=parent_hash))


# Remember to invoke the function at the end of the script to execute the pipeline!
test_orchestration()
