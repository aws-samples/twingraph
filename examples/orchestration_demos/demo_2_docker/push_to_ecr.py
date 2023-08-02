######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################


from twingraph.awsmodules.ecr.push_to_ecr import create_ecr_repo
import os

repositoryName='demo2'
try:
    create_ecr_repo(repositoryName=repositoryName)
except Exception as e:
    #print(e)
    pass

os.system('aws ecr get-login-password --region <AWS-REGION-ID> | docker login --username AWS --password-stdin <AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com')

from twingraph.docker.docker_utils import tag_image, push_image

tag_image(image_name=repositoryName+':latest',repo_name='<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/'+repositoryName+':latest', repo_tag='latest')

push_image('<AWS-ACCOUNT-ID>.dkr.ecr.<AWS-REGION-ID>.amazonaws.com/'+repositoryName+':latest', 'latest')