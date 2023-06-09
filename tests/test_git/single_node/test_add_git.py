import pytest
from twingraph import component, pipeline
import numpy
import time
import subprocess
from git_pipeline import pipeline_git

TOL = 1E-6

@pytest.mark.parametrize(('first', 'second', 'expected'), [
    (1, 2, 3),
    (2, 4, 6),
    (-2, -3, -5),
    (-5, 5, 0),
])
def test_git(first, second, expected):
    """Test with parametrization."""
    numpy.savetxt('inputs_pipeline_2.csv', [first, second])
    pipeline_git()
    time.sleep(2)
    value = numpy.loadtxt('outputs_pipeline_2.csv')
    subprocess.run(['rm','inputs_pipeline_2.csv'])   
    subprocess.run(['rm','outputs_pipeline_2.csv'])
    assert abs(value - expected) < TOL
