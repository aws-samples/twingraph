import pytest
import numpy
import time
import subprocess
from celery_pipeline import pipeline_celery_local
from pathlib import Path

import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path2= os.getcwd()
TOL = 1E-6


@pytest.mark.parametrize(('first', 'second'), [
    (2, 67)
])
def test_local(first, second):
    """Test with parametrization."""
    numpy.savetxt(dir_path+'/inputs_pipeline_celery_local.csv', [first, second])
    subprocess.run(['python', dir_path+'/celery_pipeline.py'])
    time.sleep(30)
    value = numpy.loadtxt(dir_path+'/outputs_pipeline_celery_local.csv')
    subprocess.run(['rm',dir_path+'/inputs_pipeline_celery_local.csv'])   
    subprocess.run(['rm',dir_path+'/outputs_pipeline_celery_local.csv']) 
    assert abs(value - first * (first + second)) < TOL