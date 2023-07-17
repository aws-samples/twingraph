# Known Issues and Limitations


## Limitations

- Every component needs to use NamedTuple (from collections) return type with the name of the namedtuple set to 'outputs'.

- When setting a large number of Celery concurrent tasks, it takes a long time to start up.

- Parent hashes have to be specified manually (alternatively, auto-infer can be used, but does not work with Celery).

- It is preferable to use keywords specifiers when calling functions.

- AWS Cli has to be configured outside of TwinGraph, and resources provisioned (instructions given when needed for demos).

- Currently only 1 celery control node is used, this could be improved in future releases.

- When using AWS Lambda, inputs/outputs have to be a limited size or the "extended_output" flag should be set to "True"; however this is not advisable for high concurrency tasks due to CloudWatch limitations.

- When running with GPUs locally, the Docker option needs modification with resource sets for launch (this should work seamlessly for cloud deployments with number of GPUs specification for Batch and EKS)

## Issues

- Auto-infer keyword does not work with Celery.

- When setting a large number of concurrent Celery workers (>512), there may be issues with parallel os file writes. 

- Error messages printed by Celery when remote execution (Docker, AWS Batch, Kubernetes or AWS Lambda) may be misleading - please check the appropriate console page or Kubernetes admin panel to diagnose the issues correctly.
