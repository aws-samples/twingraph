######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

import boto3
import time
import random

def exponential_backoff(base_delay, exponent, try_id):
    return random.uniform(0, (base_delay)**(try_id*exponent))

def matching_parentheses(string):
    op = []
    dc = {
        op.pop() if op else -1: i for i, c in enumerate(string) if
        (c == '(' and op.append(i) and False) or (c == ')' and op)
    }
    return False if dc.get(-1) or op else dc

def create_lambd_function(function_name, docker_image, iam_role, architecture, storage_size, memory_size, timeout):
    client = boto3.client('lambda')
    response = client.create_function(
        FunctionName=function_name,
        Role=iam_role,
        Code={
            'ImageUri': docker_image
        },
        Timeout=timeout,
        MemorySize=memory_size,
        PackageType='Image',
        ImageConfig={
        },
        Architectures=[
            architecture,
        ],
        EphemeralStorage={
            'Size': storage_size
        },
        SnapStart={
            'ApplyOn': 'None'
        }
    )
    return response


def invoke_lambd_function(function_name, python_str, region, hash, extended_output):
    client = boto3.client('lambda')
    import base64
    Unfinished = True
    try_id=0
    max_retries=15
    while Unfinished and try_id<max_retries:
        time.sleep(min(exponential_backoff(base_delay=2,exponent=1,try_id=try_id), 240))
        try:
            response = client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload='{\"python_str\": \"' + python_str + '\", \"hash\": \"' + hash + '\"}',
                LogType='Tail'
            )
            if extended_output.capitalize() =='False' and 'outputs' in str(base64.b64decode(response['LogResult'])).split('\\n')[-5]:
                Unfinished = False
                output_line = str(base64.b64decode(response['LogResult'])).split('\\n')[-5]
                output_str = output_line[:matching_parentheses(output_line)[7]+1]
                return output_str
            elif extended_output.capitalize() =='True':
                Unfinished = False
        except Exception as e:
            #print(e)
            pass
        try_id+=1
        #print('***** Lambda Function Definition Try:',try_id)

    logName = str(base64.b64decode(response['LogResult'])).split('\\n')[-4]
    
    if extended_output.capitalize() =='False':
        pass
    else:
        cloudwatch = boto3.client(
            service_name='logs',
            region_name=region,
            endpoint_url='https://logs.' + region + '.amazonaws.com')

        obtainedOutputs = False
        try_id=0
        max_retries=25
        while obtainedOutputs == False and try_id<max_retries:
            time.sleep(min(exponential_backoff(base_delay=1.5,exponent=1,try_id=try_id), 240))
            try:
                outputs = cloudwatch.get_log_events(
                    logGroupName='/aws/lambda/' + function_name,
                    logStreamName=logName.replace('CLOUDWATCHER ', '').replace(
                        ' OBTAINED_CLOUDWATCHER', '').replace(
                        ' '+hash, ''),
                    startFromHead=True,
                    unmask=True)
                if ('outputs' in outputs['events'][-4]['message']):
                    obtainedOutputs = True
            except:
                pass
            try_id+=1
            #print('***** Lambda Invocation Try:',try_id)

        return outputs['events'][-4]['message']
