######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

import docker


def get_client():
    return docker.from_env()


def build_image(dockerfile_path, dockerfile_name, image_tag):
    client = get_client()
    client.containers.prune()
    client.images.build(path=dockerfile_path,
                        dockerfile=dockerfile_name, tag=image_tag)
    return 0


def tag_image(image_name, repo_name, repo_tag):
    client = get_client()
    client.images.get(image_name).tag(repository=repo_name, tag=repo_tag)


def push_image(repo_name, repo_tag):
    client = get_client()
    client.images.push(repository=repo_name, tag=repo_tag)
    return 0
