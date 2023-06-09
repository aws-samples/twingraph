import pytest
import numpy
import time
import subprocess
from celery_pipeline_docker import pipeline_celery_docker
from pathlib import Path

import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path2= os.getcwd()
TOL = 1E-6


@pytest.mark.parametrize(('first', 'second'), [
    (2, 67)
])
def test_docker(first, second):
    """Test with parametrization."""
    numpy.savetxt(dir_path+'/inputs_pipeline_celery_docker.csv', [first, second])
    subprocess.run(['python', dir_path+'/celery_pipeline_docker.py'])
    time.sleep(30)
    value = numpy.loadtxt(dir_path+'/outputs_pipeline_celery_docker.csv')
    subprocess.run(['rm',dir_path+'/inputs_pipeline_celery_docker.csv'])   
    subprocess.run(['rm',dir_path+'/outputs_pipeline_celery_docker.csv']) 
    assert abs(value - first * (first + second)) < TOL
