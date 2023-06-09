# API Documentation

## There are two exposed API calls from TwinGraph:

-   [pipeline](#pipeline)
-   [component](#component)

<a name="pipeline"></a> 
## Pipeline Function
```Python
def pipeline( lambda_pipeline=False, batch_pipeline=False,
kubernetes_pipeline=False, celery_pipeline=False,
celery_concurrency_threads=32, celery_include_files=[],
celery_host='@localhost', celery_worker_name='tasks',
celery_backend='redis://localhost:6379/0',
celery_broker='redis://localhost:6379/1', celery_task_dir='/tmp',
graph_config={}, clear_graph=True, multipipeline=False, f_py=None,
redirect_logging=True): 
```
[Source](../twingraph/orchestration/orchestration_tools.py#L27)

[](#pipeline)

The pipeline function is intended as a decorator to an orchestration specification function, which strings together different component within a pure Python code. 

In plain form, without specifying Celery pipeline, or a remote AWS execution environment, it simply produces a Gremlin graph tracing the control flow and intermediate, either with Apache TinkerGraph or Amazon Neptune. 

When used with Celery (celery_pipeline=True), parses the pipeline and submits jobs when the component functions are initialized (delay/apply_async), and performs a synchronization wait for the result when the function is called (get). 

### Args:

-   lambda_pipeline (bool, optional): *This flag is used to specify if
    any components within the pipeline are run with AWS Lambda; when
    using this ensure that the component functions have associated
    lambda_task flags set with lambda_config parameters.* Defaults to
    False.

-   batch_pipeline (bool, optional): *This flag is used to specify if
    any components within the pipeline are run with AWS Batch; when
    using this ensure that the component functions have associated
    batch_task flags set with batch_config parameters.* Defaults to
    False.

-   kubernetes_pipeline (bool, optional): *This flag is used to specify
    if any components within the pipeline are run with Kubernetes, with
    Kubectl pointed to the right execution environment; when using this
    ensure that the component functions have associated kubernetes_task
    flags set with kube_config parameters.* Defaults to False.

-   celery_pipeline (bool, optional): *This flag sets whether the
    pipeline is executed directly or parsed into a Celery orchestration
    pipeline. Celery is the backend queueing, dispatch and orchestration
    engine; without Celery the tasks are simply run locally - hence,
    ensure that this flag is set to true for executing remotely.*
    Defaults to False.

-   celery_concurrency_threads (int, optional): *When using a Celery
    pipeline, a set number of tasks can be concurrently executed - this
    can be tuned using this flag.* Defaults to 32.

-   celery_include_files (list, optional): *When using Celery-based
    components, ensure that the files which contain any of these
    components are specified here in order to parse and extract
    information.* Defaults to [].

-   celery_host (str, optional): *Celery can be hosted locally or on a
    remote cluster (eg. EKS) for resilience and fault tolerance; if not
    hosted locally, specify using this string.* Defaults to
    "@localhost".

-   celery_worker_name (str, optional): *This optional string changes
    the name of the celery workers, in case there are other concurrently
    running Celery tasks and collisions need to be avoided.* Defaults to
    "tasks".

-   celery_backend (str, optional): *This string specifies the backend
    result store service URL, based on either Redis, RabbitMQ/PyAMQ
    (RPC), SQLAlchemy or a custom MQ/Database - when using the default
    Redis ensure that redis-cli ping returns PONG.* Defaults to
    'redis://localhost:6379/0'.

-   celery_broker (str, optional): *This string specifies the backend
    message broker service URL, based on either Redis, RabbitMQ/PyAMQ,
    AWS SQS or a custom MQ - when using the default Redis ensure that
    redis-cli ping returns PONG.* Defaults to
    'redis://localhost:6379/1'.

-   celery_task_dir (str, optional): *When using Celery, this string
    determines where the tasks are executed and stored; if using the
    default tmp directory ensure that you have read/write access -
    otherwise change this directory to another local directory.*
    Defaults to '/tmp'.

-   graph_config (dict, optional): *This dictionary includes a
    parameter called graph_endpoint, which needs to point to the URL
    endpoint of the graph, including the websocket protocol (ws, wss)
    and the port ID (usually 8182).* Defaults to
    {'graph_endpoint':'ws://localhost:8182'}.

-   clear_graph (bool, optional): *This flag will clear the backend
    graph (Apache TinkerGraph or Amazon Neptune) before executing the
    pipeline.* Defaults to True.

-   multipipeline (bool, optional): *Ensure that this flag is on when
    running multiple concurrent pipelines to ensure that there are no
    collisions and the graphs are not cleared.* Defaults to False.

-   f_py (_type_, optional): *This in a method for feeding the
    function without using the pipeline as a decorator - at the moment
    not supported due to parsing limitations.* Defaults to None.

-   redirect_logging (bool, optional): *Ensure that this flag is set to
    on in order to get verbose information logs from Celery; however if
    using Ray or another library which also prints logs to the same
    directory, this needs to be set to False.* Defaults to True.

### Raises:

-   Exception: If the pipeline includes Kubernetes, Lambda or Batch
    tasks but is not set to a Celery pipeline.

-   Exception: If the number of Celery concurrency threads is too high
    that the local machine runs out of resources.

-   Exception: If the Celery host cannot be found or is not running.

### Returns:

-   None: Without Celery, an output can specified. With Celery, the
    pipeline does not return any outputs, it converts the pipeline logic
    to a Celery control flow.

<a name="component"></a> 
## Component Function 
```Python
def component(lambda_task=False, batch_task=False,
kubernetes_task=False, f_py=None, docker_id='NotProvided',
kube_config={}, batch_config={}, lambda_config={}, graph_config={},
additional_attributes={}, git_data=False, auto_infer=False): 
```
[Source](../twingraph/orchestration/orchestration_tools.py#L213)

The component function is intended to be used as a decorator on top of Python functions which read basic json-pickleable data types (int, float, lists, strings) and return NamedTuples called 'outputs' converted into dictionaries containing 'hash' and 'outputs'. Using appropriate flag and configuration dictionary pairs, such as lambda_task+lambda_config, batch_task+batch_config or kubernetes_task+kube_config, the code will be stringified and run on the selected backend compute. Additionally, the graph backend used to record the task can be switched (i.e. Amazon Neptune or Apache TinkerGraph) 

### Args: 

-   lambda_task (bool, optional): *This flag indicates if the component
    Python code should be executed on AWS Lambda.* Defaults to False.

-   batch_task (bool, optional): *This flag indicates if the component
    Python code should be executed on AWS Batch.* Defaults to False.

-   kubernetes_task (bool, optional): *This flag indicates if the
    component Python code should be executed on the Kubernetes backend
    configured by Kubectl.* Defaults to False.

-   f_py (_type_, optional): *This is an experimental method to pass
    in repeated functions instead of defining new ones for different
    parameters, however this is unsupported with Celery due to parsing
    issues.* Defaults to None.

-   docker_id (str, optional): *This string specifies the ID of the
    docker image, and the function will be executed within the docker
    container launched from the image.* Defaults to 'NotProvided'.

-   kube_config (dict, optional): *This dictionary includes information
    needed to execute Kubernetes tasks - information that can be passed
    include, for example: {"pull_policy": "Always","namespace":
    "default", "timeout":"360000"} .* Defaults to {"pull_policy":
    "Always","namespace": "default", "timeout":"360000"} - does not need
    to be specified explicitly with the kubernetes_task flag.

-   batch_config (dict, optional): *This dictionary includes
    information needed to execute AWS Batch tasks - information that can
    be passed include, for example: {"region_name": "", "jobQueue":
    "twingraph-run-queue","logGroupName": "/aws/batch/job","vCPU":
    1,"Mem": 2048}. The default and supported environment is ECS/EC2 - for Fargate specify two additional parameters "roleARN" based on [this reference](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html) and "envType" as "fargate"; EKS on Batch is unsupported.* Defaults to {} - needs to be specified explicitly
    with the batch_task flag.

-   lambda_config (dict, optional): *This dictionary includes
    information needed to execute AWS Lambda tasks - information that
    can be passed include, for example: {"iam_role":
    "ROLE-ARN", "architecture": "x86_64","storage_size":
    512, "region_name": "", "timeout": 900}. One additional parameter which allows for larger outputs for Lambda tasks is "extended_output" set to "True", however this can result in log collisions when retrieving outputs with high concurrency running the same function.* Defaults to {} - needs to
    be specified explicitly with the lambda_task flag.

-   graph_config (dict, optional): *This dictionary includes a
    parameter called graph_endpoint, which needs to point to the URL
    endpoint of the graph, including the websocket protocol (ws, wss)
    and the port ID (usually 8182).* Defaults to
    {'graph_endpoint':'ws://localhost:8182'}.

-   additional_attributes (dict, optional): *This dictionary can be
    optionally specified by the user to include any information about
    additional attributes known prior to execution associated with this
    component which need to be recorded on the graph database.* Defaults
    to {}.

-   git_data (bool, optional): *This flag allows the user to
    automatically record git data about the function (author, timestamp
    changelog) to the graph database.* Defaults to False.

-   auto_infer (bool, optional): *This is an experimental flag which
    allows the user to automatically infer the task chain and
    interdependencies, but it does not work with Celery due to stack
    visibility issues for security reasons.* Defaults to False.

### Raises: 

-   Exception: Only one task execution should be specified at once
    either lambda_task, batch_task or kubernetes_task but not two of
    them at the same time.

-   Exception: If git data is used but git is not installed.

-   Exception: If the configuration does not match the task description
    e.g. Batch with non-Batch config, etc.

-   Exception: If autoinfer is used with Celery.

### Returns: 

-   Dict (from NamedTuple function definition): The components need to be
    specified with a NamedTuple return in the function definition, but
    TwinGraph converts the outputs into a Python dictionary with two
    components - 'hash' which includes a string indicating component
    hash as it was run, and 'outputs' which contains all the return
    values contained within the NamedTuple used in the function
    definition.

