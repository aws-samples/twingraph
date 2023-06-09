import pytest
from twingraph import component, pipeline
import numpy
import time
import subprocess
from add_multiply_pipeline import pipeline_1

TOL = 1E-6

@pytest.mark.parametrize(('first', 'second'), [
    (1, 2),
    (2, 4),
    (-2, -3),
    (-5, 5),
])
def test_local(first, second):
    """Test with parametrization."""
    numpy.savetxt('inputs_pipeline_1.csv', [first, second])
    pipeline_1()
    time.sleep(2)
    value = numpy.loadtxt('outputs_pipeline_1.csv')
    subprocess.run(['rm','inputs_pipeline_1.csv'])   
    subprocess.run(['rm','outputs_pipeline_1.csv'])
    assert abs(value - first*(first+second)) < TOL
