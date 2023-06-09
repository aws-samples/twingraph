######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

import sys
import time
from datetime import datetime
import random

import boto3
from botocore.compat import total_seconds
import os

from twingraph.awsmodules.cloudwatch.cloudwatch_utils import get_cloudwatch_client

from twingraph.awsmodules.awslambda.lambd_functions import exponential_backoff

def printLogs(logGroupName, logStreamName, startTime, regionName):
    kwargs = {'logGroupName': logGroupName,
              'logStreamName': logStreamName,
              'startTime': startTime,
              'startFromHead': True}

    cloudwatch = boto3.client(
        service_name='logs',
        region_name=regionName,
        endpoint_url='https://logs.' + regionName + '.amazonaws.com')

    lastTimestamp = 0.
    while True:
        logEvents = cloudwatch.get_log_events(**kwargs)

        for event in logEvents['events']:
            lastTimestamp = event['timestamp']
            timestamp = datetime.utcfromtimestamp(
                lastTimestamp / 1000.0).isoformat()
            # print('[%s] %s' % ((timestamp + ".000")[:23] + 'Z', event['message']))

        nextToken = logEvents['nextForwardToken']
        if nextToken and kwargs.get('nextToken') != nextToken:
            kwargs['nextToken'] = nextToken
        else:
            break
    return lastTimestamp


def getLogStream(logGroupName, jobName, jobId, regionName):

    cloudwatch = boto3.client(
        service_name='logs',
        region_name=regionName,
        endpoint_url='https://logs.' + regionName + '.amazonaws.com')

    response = cloudwatch.describe_log_streams(
        logGroupName=logGroupName,
        logStreamNamePrefix=jobName + '/' + jobId
    )
    logStreams = response['logStreams']

    if not logStreams:
        return ''
    else:
        return logStreams[0]['logStreamName']


def nowInMillis():
    endTime = (total_seconds(datetime.utcnow() - datetime(1970, 1, 1))) * 1000
    return endTime


def submit_job(logGroupName, jobName, jobQueue, jobDefinition, command, regionName, wait=True):
    batch = boto3.client(
        service_name='batch',
        region_name=regionName,
        endpoint_url='https://batch.' + regionName + '.amazonaws.com')

    # jitter to avoid API flooding, time for cloudwatch to register
    submittedJob = False
    try_id=0
    max_retries=5
    while submittedJob == False and try_id<max_retries:
        time.sleep(exponential_backoff(base_delay=1.5,exponent=1.2,try_id=try_id))
        #print('Submitting Job Try:',try_id)
        try:
            submitJobResponse = batch.submit_job(
                jobName=jobName,
                jobQueue=jobQueue,
                jobDefinition=jobDefinition,
                containerOverrides={'command': command}
            )
            jobId = submitJobResponse['jobId']
            submittedJob=True
        except Exception as e:
            #print('submit job try:',try_id,e)
            pass
        try_id+=1

    # print('Submitted job [%s - %s] to the job queue [%s]' % (jobName, jobId, jobQueue))

    spinner = 0
    running = False
    startTime = 0

    # jitter to avoid API flooding, time for cloudwatch to register
    try_id=0
    max_retries=35
    while wait and try_id<max_retries:
        time.sleep(min(exponential_backoff(base_delay=1.5,exponent=1.1,try_id=try_id),900))  
        try:
            describeJobsResponse = batch.describe_jobs(jobs=[jobId])
            status = describeJobsResponse['jobs'][0]['status']
            if status == 'SUCCEEDED':
                print('%s' % ('=' * 80))
                print('Job [%s - %s] %s' % (jobName, jobId, status))
                logStreamName = getLogStream(
                    logGroupName, jobName, jobId, regionName)
                wait=False
                return describeJobsResponse['jobs'][0]['container']['logStreamName']
            elif status == 'FAILED':
                print('%s' % ('=' * 80))
                print('Job [%s - %s] %s' % (jobName, jobId, status))
                logStreamName = getLogStream(
                    logGroupName, jobName, jobId, regionName)
                print(describeJobsResponse['jobs'][0]['container']['logStreamName'])
                print('Batch job failed, check Batch console',
                    describeJobsResponse['jobs'][0]['attempts'][-1])
                os.system("pkill -9 -f 'celerytasks'")
                wait=False
            elif status == 'RUNNING':
                logStreamName = getLogStream(
                    logGroupName, jobName, jobId, regionName)
                if not running and logStreamName:
                    running = True
                    # print('\rJob [%s - %s] is RUNNING.' % (jobName, jobId))
                    # print('Output [%s]:\n %s' % (logStreamName, '=' * 80))
                if logStreamName:
                    startTime = printLogs(
                        logGroupName, logStreamName, startTime, regionName) + 1
                    # print(logGroupName, logStreamName)
            else:
                # print('\rJob [%s - %s] is %-9s... %s' % (jobName, jobId, status, spin[spinner % len(spin)])),
                sys.stdout.flush()
                spinner += 1
        except Exception as e:
            # print('wait results Try '+str(try_id),e)
            pass
        try_id+=1
            
def obtain_results(batch_config, cw_log_name):
    # jitter to avoid API flooding, time for cloudwatch to register
    obtainedOutputs = False
    try_id=0
    max_retries=15
    output_str = ''
    while obtainedOutputs == False and try_id<max_retries:
        time.sleep(exponential_backoff(base_delay=2,exponent=1.2,try_id=try_id))
        try:
            cloudwatch = get_cloudwatch_client(batch_config['region_name'])
            response = cloudwatch.describe_log_streams(
                logGroupName=batch_config['logGroupName'],
                logStreamNamePrefix=cw_log_name
            )

            kwargs = {'logGroupName': batch_config['logGroupName'],
                      'logStreamName': response['logStreams'][0]['logStreamName'],
                      'startTime': 0,
                      'startFromHead': True}

            output_str = str(cloudwatch.get_log_events(
                **kwargs)['events'][-1]['message'])
            
            if ('outputs' in output_str):
                obtainedOutputs = True 
        except Exception as e:
            #print('obtain results Try '+str(try_id),e)
            pass
        
        try_id+=1
        
    return output_str
