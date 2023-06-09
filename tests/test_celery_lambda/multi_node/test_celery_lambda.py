import pytest
import numpy
import time
import subprocess
from pathlib import Path
import os 
from twingraph.awsmodules.awslambda.lambd_functions import exponential_backoff

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path2= os.getcwd()
TOL = 1E-6

@pytest.mark.parametrize(('first', 'second'), [
    (2, 67)
])
def test_lambda(first, second):
    max_retries = 50
    try:
        import boto3
        client = boto3.client('sts')
        response_dict = client.get_caller_identity()
        response = response_dict['Arn']
    except:
        response = 'Unknown'
    
    if response == 'Unknown':
        assert 1
    else:
        """Test with parametrization."""
        numpy.savetxt(dir_path+'/inputs_pipeline_celery_lambda.csv', [first, second])
        subprocess.run(['python', dir_path+'/celery_pipeline_lambda.py'])
        try_id = 0
        unfinished = 1
        value=0
        while try_id < max_retries and unfinished:
            time.sleep(min(exponential_backoff(1.2,1.2,try_id=try_id),60))
            try:
                value = numpy.loadtxt(dir_path+'/outputs_pipeline_celery_lambda.csv')
                unfinished = 0
                assert abs(value - first * (first + second)) < TOL
            except:
                pass
            try_id+=1
        try:
            subprocess.run(['rm',dir_path+'/inputs_pipeline_celery_lambda.csv'])   
            subprocess.run(['rm',dir_path+'/outputs_pipeline_celery_lambda.csv']) 
        except:
            pass
        

