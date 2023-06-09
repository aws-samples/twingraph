import pytest
import numpy
import time
import subprocess
from pathlib import Path
from kubernetes import client, config, watch
import os 
from twingraph.awsmodules.awslambda.lambd_functions import exponential_backoff

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path2= os.getcwd()
TOL = 1E-6

@pytest.mark.parametrize(('first', 'second'), [
    (2, 67)
])
def test_k8s(first, second):
    config.load_kube_config()
    kube_client = client.CoreV1Api()
    max_retries = 50

    node_list = kube_client.list_node(watch=False, pretty=True, limit=1000)
    if len(node_list.items) > 0:
        """Test with parametrization."""
        numpy.savetxt(dir_path+'/inputs_pipeline_celery_k8s.csv', [first, second])
        subprocess.run(['python', dir_path+'/celery_pipeline_k8s.py'])
        try_id = 0
        unfinished = 1
        while try_id < max_retries and unfinished:
            time.sleep(min(exponential_backoff(1.2,1.2,try_id=try_id),60))
            try:
                value = numpy.loadtxt(dir_path+'/outputs_pipeline_celery_k8s.csv')
                assert abs(value - first * (first + second)) < TOL
                unfinished = 0
            except Exception as e:
                pass
            try_id+=1
        if unfinished:
            assert 0
    else:
        print("No nodes available in the cluster")
        assert 1
    try:
        subprocess.run(['rm',dir_path+'/inputs_pipeline_celery_k8s.csv'])   
        subprocess.run(['rm',dir_path+'/outputs_pipeline_celery_k8s.csv']) 
    except:
        pass

