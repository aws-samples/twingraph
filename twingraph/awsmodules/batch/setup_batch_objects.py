######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

import boto3
import time
import sys


def create_compute_environment(computeEnvironmentName, computeEnvironmentType, instanceType, unitVCpus, imageId, serviceRole, instanceRole, subnets, securityGroups, regionName):
    batch = boto3.client(
        service_name='batch',
        region_name=regionName,
        endpoint_url='https://batch.' + regionName + '.amazonaws.com')
    response = batch.create_compute_environment(
        computeEnvironmentName=computeEnvironmentName,
        type='MANAGED',
        serviceRole=serviceRole,
        computeResources={
            'type': computeEnvironmentType,
            'imageId': imageId,
            'minvCpus': unitVCpus * 1,
            'maxvCpus': unitVCpus * 2,
            'desiredvCpus': unitVCpus * 1,
            'instanceTypes': [instanceType],
            'subnets': subnets,
            'securityGroupIds': securityGroups,
            'instanceRole': instanceRole
        }
    )

    spinner = 0
    while True:
        describe = batch.describe_compute_environments(
            computeEnvironments=[computeEnvironmentName])
        computeEnvironment = describe['computeEnvironments'][0]
        status = computeEnvironment['status']
        if status == 'VALID':
            print('\rSuccessfully created compute environment %s' %
                  (computeEnvironmentName))
            break
        elif status == 'INVALID':
            reason = computeEnvironment['statusReason']
            raise Exception(
                'Failed to create compute environment: %s' % (reason))
        sys.stdout.flush()
        spinner += 1
        time.sleep(1)

    return response


def create_job_queue(computeEnvironmentName, queueName, regionName):
    jobQueueName = queueName
    batch = boto3.client(
        service_name='batch',
        region_name=regionName,
        endpoint_url='https://batch.' + regionName + '.amazonaws.com')
    response = batch.create_job_queue(jobQueueName=jobQueueName,
                                      priority=0,
                                      computeEnvironmentOrder=[
                                          {
                                              'order': 0,
                                              'computeEnvironment': computeEnvironmentName
                                          }
                                      ])

    spinner = 0
    while True:
        describe = batch.describe_job_queues(jobQueues=[jobQueueName])
        jobQueue = describe['jobQueues'][0]
        status = jobQueue['status']
        if status == 'VALID':
            print('\rSuccessfully created job queue %s' % (jobQueueName))
            break
        elif status == 'INVALID':
            reason = jobQueue['statusReason']
            raise Exception('Failed to create job queue: %s' % reason)
        sys.stdout.flush()
        spinner += 1
        time.sleep(1)

    return response


def register_job_definition(jobDefName, image, unitVCpus, unitMemory, regionName, numGPUs, envType, roleARN):
    batch = boto3.client(
        service_name='batch',
        region_name=regionName,
        endpoint_url='https://batch.' + regionName + '.amazonaws.com')
    if envType.upper() == 'FARGATE':
        response = batch.register_job_definition(jobDefinitionName=jobDefName,
                                                 type='container',
                                                 platformCapabilities=[
                                                'FARGATE',
                                                ],         
                                                 containerProperties={
                                                     'image': image,
                                                     "executionRoleArn": roleARN,
                                                     'resourceRequirements': [
                                                         {
                                                             'type': 'MEMORY',
                                                             'value': str(unitMemory),
                                                         },
                                                         {
                                                             'type': 'VCPU',
                                                             'value': str(unitVCpus),
                                                         },
                                                     ],
                                                 })
    elif numGPUs == 0:
        response = batch.register_job_definition(jobDefinitionName=jobDefName,
                                                 type='container',
                                                 containerProperties={
                                                     'image': image,
                                                     'privileged': True,
                                                     'resourceRequirements': [
                                                         {
                                                             'type': 'MEMORY',
                                                             'value': str(unitMemory),
                                                         },
                                                         {
                                                             'type': 'VCPU',
                                                             'value': str(unitVCpus),
                                                         },
                                                     ],
                                                 })
    else:
        response = batch.register_job_definition(jobDefinitionName=jobDefName,
                                                 type='container',
                                                 containerProperties={
                                                     'image': image,
                                                     'privileged': True,
                                                     'resourceRequirements': [
                                                         {
                                                             'value': str(numGPUs),
                                                             'type': 'GPU'
                                                         },
                                                         {
                                                             'type': 'MEMORY',
                                                             'value': str(unitMemory),
                                                         },
                                                         {
                                                             'type': 'VCPU',
                                                             'value': str(unitVCpus),
                                                         },
                                                     ],
                                                     #  'volumes': [
                                                     #      {
                                                     #          'host': {
                                                     #              'sourcePath': '/var/lib/nvidia-docker/volumes/nvidia_driver/latest'
                                                     #          },
                                                     #          'name': 'nvidia-driver-dir'
                                                     #      }
                                                     # ],
                                                     #  'mountPoints': [
                                                     #      {
                                                     #          'containerPath': '/usr/local/nvidia',
                                                     #          'readOnly': True,
                                                     #          'sourceVolume': 'nvidia-driver-dir'
                                                     #      }
                                                     #  ]
                                                 })
    return response
