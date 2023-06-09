######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

import logging
from kubernetes import client, config, watch

logging.basicConfig(level=logging.INFO)

try:
    config.load_kube_config()
except:
    print('Kubernetes configuration not loaded.')
    pass


# Init Kubernetes
core_api = client.CoreV1Api()
batch_api = client.BatchV1Api()


def create_namespace(namespace):

    namespaces = core_api.list_namespace()
    all_namespaces = []
    for ns in namespaces.items:
        all_namespaces.append(ns.metadata.name)

    if namespace in all_namespaces:
        logging.info(f"Namespace {namespace} already exists. Reusing.")
    else:
        namespace_metadata = client.V1ObjectMeta(name=namespace)
        core_api.create_namespace(
            client.V1Namespace(metadata=namespace_metadata)
        )
        logging.info(f"Created namespace {namespace}.")

    return namespace


def create_container(image, name, pull_policy, command, args):

    container = client.V1Container(
        image=image,
        name=name,
        image_pull_policy=pull_policy,
        args=args,
        command=command,
    )

    return container


def create_pod_template(pod_name, container):
    pod_template = client.V1PodTemplateSpec(
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
        metadata=client.V1ObjectMeta(name=pod_name, labels={
                                     "pod_name": pod_name}),
    )

    return pod_template


def create_job(job_name, pod_template):
    metadata = client.V1ObjectMeta(name=job_name, labels={"job_name": job_name})

    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=metadata,
        spec=client.V1JobSpec(backoff_limit=0, template=pod_template),
    )

    return job

