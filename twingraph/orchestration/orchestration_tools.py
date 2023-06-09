######################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. #
# SPDX-License-Identifier: MIT-0                                     #
######################################################################

import nest_asyncio
import functools
import inspect

from pathlib import Path
from twingraph.graph.graph_tools import init_reset_graph, add_vertex_connection
from twingraph.orchestration.orchestration_utils import remove_line_containing, set_gremlin_port_ip, set_randomize_time, run_aws_batch, batch_create_component, lambda_create_component, load_inputs, set_hash, set_AWS_ARN, line_no, run_kubernetes, run_lambda, run_docker_compose
from twingraph.awsmodules.awslambda.lambd_functions import exponential_backoff, matching_parentheses

from collections import namedtuple
import hashlib
import datetime
import time
import random
import os
import json
import ast
import shutil
import string
import subprocess


def pipeline(lambda_pipeline=False, batch_pipeline=False, kubernetes_pipeline=False, celery_pipeline=False, celery_concurrency_threads=32, celery_include_files=[], celery_host="@localhost", celery_worker_name="tasks", celery_backend='redis://localhost:6379/0', celery_broker='redis://localhost:6379/1', celery_task_dir='/tmp', graph_config={}, clear_graph=True, multipipeline=False, f_py=None, redirect_logging=True):
    """ 
    ### The pipeline function is intended as a decorator to an orchestration specification function, which strings together different component within a pure python code. 
    
    ### In plain form, without specifying Celery pipeline, or a remote AWS execution environment, it simply produces a Gremlin graph tracing the control flow and intermediate, either with Apache TinkerGraph or Amazon Neptune. 
    
    ### When used with Celery (celery_pipeline=True), parses the pipeline and submits jobs when the component functions are initialized (delay/apply_async), and performs a synchronization wait for the result when the function is called (get).

    ### Args:
    
    - lambda_pipeline (bool, optional): *This flag is used to specify if any components within the pipeline are run with AWS Lambda; when using this ensure that the component functions have associated lambda_task flags set with lambda_config parameters.* Defaults to False.
    
    - batch_pipeline (bool, optional): *This flag is used to specify if any components within the pipeline are run with AWS Batch; when using this ensure that the component functions have associated batch_task flags set with batch_config parameters.* Defaults to False.
    
    - kubernetes_pipeline (bool, optional): *This flag is used to specify if any components within the pipeline are run with Kubernetes, with Kubectl pointed to the right execution environment; when using this ensure that the component functions have associated kubernetes_task flags set with kube_config parameters.* Defaults to False.
        
    - celery_pipeline (bool, optional): *This flag sets whether the pipeline is executed directly or parsed into a Celery orchestration pipeline. Celery is the backend queueing, dispatch and orchestration engine; without Celery the tasks are simply run locally - hence, ensure that this flag is set to true for executing remotely.* Defaults to False.
    
    - celery_concurrency_threads (int, optional): *When using a Celery pipeline, a set number of tasks can be concurrently executed - this can be tuned using this flag.* Defaults to 32.
    
    - celery_include_files (list, optional): *When using Celery-based components, ensure that the files which contain any of these components are specified here in order to parse and extract information.* Defaults to [].
    
    - celery_host (str, optional): *Celery can be hosted locally or on a remote cluster (eg. EKS) for resilience and fault tolerance; if not hosted locally, specify using this string.* Defaults to "@localhost".
    
    - celery_worker_name (str, optional): *This optional string changes the name of the celery workers, in case there are other concurrently running Celery tasks and collisions need to be avoided.* Defaults to "tasks".
    
    - celery_backend (str, optional): *This string specifies the backend result store service URL, based on either Redis, RabbitMQ/PyAMQ (RPC), SQLAlchemy or a custom MQ/Database - when using the default Redis ensure that redis-cli ping returns PONG.* Defaults to 'redis://localhost:6379/0'.
        
    - celery_broker (str, optional): *This string specifies the backend message broker service URL, based on either Redis, RabbitMQ/PyAMQ, AWS SQS or a custom MQ - when using the default Redis ensure that redis-cli ping returns PONG.* Defaults to 'redis://localhost:6379/1'.
    
    - celery_task_dir (str, optional): *When using Celery, this string determines where the tasks are executed and stored; if using the default tmp directory ensure that you have read/write access - otherwise change this directory to another local directory.* Defaults to '/tmp'.
    
    - graph_config (dict, optional): *This dictionary includes a parameter called graph_endpoint, which needs to point to the URL endpoint of the graph, including the websocket protocol (ws, wss) and the port ID (usually 8182).* Defaults to {'graph_endpoint':'ws://localhost:8182'}.
        
    - clear_graph (bool, optional): *This flag will clear the backend graph (Apache TinkerGraph or Amazon Neptune) before executing the pipeline.* Defaults to True.
        
    - multipipeline (bool, optional): *Ensure that this flag is on when running multiple concurrent pipelines to ensure that there are no collisions and the graphs are not cleared.* Defaults to False.
        
    - f_py (_type_, optional): *This in a method for feeding the function without using the pipeline as a decorator - at the moment not supported due to parsing limitations.* Defaults to None.
        
    - redirect_logging (bool, optional): *Ensure that this flag is set to on in order to get verbose information logs from Celery; however if using Ray or another library which also prints logs to the same directory, this needs to be set to False.* Defaults to True.

    ### Raises:
    
    - Exception: If the pipeline includes Kubernetes, Lambda or Batch tasks but is not set to a Celery pipeline.
    
    - Exception: If the number of Celery concurrency threads is too high that the local machine runs out of resources.
    
    - Exception: If the Celery host cannot be found or is not running.
        

    ### Returns:
    
    - None: Without Celery, an output can specified. With Celery, the pipeline does not return any outputs, it converts the pipeline logic to a Celery control flow.
    """
    
    assert callable(f_py) or f_py is None

    def _decorator(func):
        nest_asyncio.apply()
        file_path = inspect.stack()[1].filename
        path = Path(file_path)
        pipeline_name = str(func.__name__)

        if kubernetes_pipeline:
            if celery_pipeline == False:
                raise Exception(
                    "Kubernetes needs to be orchestrated with Celery!")

        if batch_pipeline:
            if celery_pipeline == False:
                raise Exception("Batch needs to be orchestrated with Celery!")

        if lambda_pipeline:
            if celery_pipeline == False:
                raise Exception("Lambda needs to be orchestrated with Celery!")

        if celery_pipeline:
            if multipipeline == False:
                try:
                    os.system("pkill -9 -f 'celerytasks'")
                except:
                    pass

            celery_include_files.append(file_path)

            encoded_pipeline_hash = hashlib.md5(
                str(datetime.datetime.now()).encode(), usedforsecurity=False)

            pipeline_dir = celery_task_dir + '/celerytasks/' + \
                pipeline_name + str(encoded_pipeline_hash.hexdigest())
            try:
                shutil.rmtree(pipeline_dir)

            except:
                pass
            os.makedirs(pipeline_dir)
            component_functions_names = []
            data = "from celery import Celery, signals\napp = Celery('" + celery_worker_name + '_' + \
                pipeline_name + "', backend='" + celery_backend + \
                "',  broker='" + celery_broker + "')\n"

            for celery_include in celery_include_files:
                with open(celery_include, 'r') as file:
                    data += '\n'
                    data_f = file.read().replace('\n@component', "\n@app.task(trail=True, queue='" +
                                                 pipeline_name + "',routing_key='" + pipeline_name + celery_host + "')\n@component")
                    data += '\n' + data_f
                    node = ast.parse(data_f)
                    component_functions_names_file = [
                        n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    component_functions_names += component_functions_names_file

            data = data.replace(inspect.getsource(func), "").replace(
                '\n' + str(func.__name__), "\n")
            data = data.replace('\n()', '')

            if redirect_logging:
                data += "@signals.setup_logging.connect\ndef setup_celery_logging(**kwargs):\n  pass\n"

            data += "if __name__ == '__main__':\n  app.worker_main(['worker','--loglevel=DEBUG','--concurrency=" + str(
                celery_concurrency_threads) + "', '-n','" + pipeline_name + celery_host + "','-Q', '" + pipeline_name + "', '-Ofair'])"

            for celery_include in celery_include_files:
                data = remove_line_containing(
                    data, celery_include.replace('.py', '').replace('/', '.'))

            print(data, file=open(pipeline_dir +
                  '/tasks_' + pipeline_name + '.py', 'w'))

            component_functions_names.remove(pipeline_name)
            component_names = list(set(component_functions_names))

            if batch_pipeline:
                json.dump(component_names, open(
                    pipeline_dir + '/components_list_batch.json', 'w'))

            if lambda_pipeline:
                json.dump(component_names, open(pipeline_dir +
                          '/components_list_lambda.json', 'w'))

            pipeline_content = 'from tasks_' + pipeline_name + ' import ' + str(component_functions_names).replace("[", '').replace(
                "]", '').replace("'", "") + '\n\n' + "\n".join((inspect.getsource(func)).split("\n")[1:]) + '\n' + str(func.__name__) + '()'

            spec_characters = list(string.punctuation)
            spec_characters.remove('_')
            spec_characters.remove('-')
            for f_name in component_functions_names:
                pipeline_content = pipeline_content.replace(
                    ' ' + f_name + '(', ' ' + f_name + '.delay(')
                for spec_character in spec_characters:
                    pipeline_content = pipeline_content.replace(
                        spec_character + f_name + '(', spec_character + f_name + '.delay(')

            pipeline_content = pipeline_content.replace(
                "['outputs']", ".get()['outputs']")
            pipeline_content = pipeline_content.replace(
                "['hash']", ".get()['hash']")

            print(pipeline_content, file=open(pipeline_dir +
                  '/pipeline_' + pipeline_name + '.py', 'w'))

            celery_task_proc = subprocess.Popen(
                ['python', pipeline_dir + '/tasks_' + pipeline_name + '.py'], cwd=str(path.parent.absolute()), shell=False)

            celery_pipeline_proc = subprocess.Popen(
                ['python', pipeline_dir + '/pipeline_' + pipeline_name + '.py'], cwd=str(path.parent.absolute()), shell=False)

            def empty_fun():
                if clear_graph:
                    gremlin_ip_port = set_gremlin_port_ip(graph_config)
                    init_reset_graph(gremlin_ip_port)
                pass
            return empty_fun
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if clear_graph:
                    gremlin_ip_port = set_gremlin_port_ip(graph_config)
                    init_reset_graph(gremlin_ip_port)
                retval = func(*args, **kwargs)
                return retval
            return wrapper
    return _decorator(f_py) if callable(f_py) else _decorator


def component(lambda_task=False, batch_task=False, kubernetes_task=False, f_py=None, docker_id='NotProvided', kube_config={}, batch_config={}, lambda_config={}, graph_config={}, additional_attributes={}, git_data=False, auto_infer=False):
    """
    ### The component function is intended to be used as a decorator on top of Python functions which read basic json-pickleable data types (int, float, lists, strings) and return NamedTuples called 'outputs' converted into dictionaries containing 'hash' and 'outputs'. Using appropriate flag and configuration dictionary pairs, such as lambda_task+lambda_config, batch_task+batch_config or kubernetes_task+kube_config, the code will be stringified and run on the selected backend compute. Additionally, the graph backend used to record the task can be switched (i.e. Amazon Neptune or Apache TinkerGraph) 

    ### Args:
    
    - lambda_task (bool, optional): *This flag indicates if the component Python code should be executed on AWS Lambda.* Defaults to False.
    
    - batch_task (bool, optional): *This flag indicates if the component Python code should be executed on AWS Batch.* Defaults to False.
    
    - kubernetes_task (bool, optional): *This flag indicates if the component Python code should be executed on the Kubernetes backend configured by Kubectl.* Defaults to False.
    
    - f_py (_type_, optional): *This is an experimental method to pass in repeated functions instead of defining new ones for different parameters, however this is unsupported with Celery due to parsing issues.* Defaults to None.
    
    - docker_id (str, optional): *This string specifies the ID of the docker image, and the function will be executed within the docker container launched from the image.* Defaults to 'NotProvided'.
    
    - kube_config (dict, optional): *This dictionary includes information needed to execute Kubernetes tasks - information that can be passed include, for example: {"pull_policy": "Always","namespace": "default", "timeout":"360000"} .* Defaults to {"pull_policy": "Always","namespace": "default", "timeout":"360000"} - does not need to be specified explicitly with the kubernetes_task flag.
    
    - batch_config (dict, optional): *This dictionary includes information needed to execute AWS Batch tasks - information that can be passed include, for example: {"region_name": "<AWS-REGION-ID>", "jobQueue": "twingraph-run-queue","logGroupName": "/aws/batch/job","vCPU": 1,"Mem": 2048} .* Defaults to {} - needs to be specified explicitly with the batch_task flag.
    
    - lambda_config (dict, optional): *This dictionary includes information needed to execute AWS Lambda tasks - information that can be passed include, for example: {"iam_role": "arn:aws:iam::<AWS-ACCOUNT-ID>:role/<AWS-LAMBDA-ROLE-ID>", "architecture": "x86_64","storage_size": 512, "region_name": "<AWS-REGION-ID>", "timeout": 900}.* Defaults to {} - needs to be specified explicitly with the lambda_task flag.
    
    - graph_config (dict, optional): *This dictionary includes a parameter called graph_endpoint, which needs to point to the URL endpoint of the graph, including the websocket protocol (ws, wss) and the port ID (usually 8182).* Defaults to {'graph_endpoint':'ws://localhost:8182'}.
    
    - additional_attributes (dict, optional): *This dictionary can be optionally specified by the user to include any information about additional attributes known prior to execution associated with this component which need to be recorded on the graph database.* Defaults to {}.
    
    - git_data (bool, optional): *This flag allows the user to automatically record git data about the function (author, timestamp changelog) to the graph database.* Defaults to False.
    
    - auto_infer (bool, optional): *This is an experimental flag which allows the user to automatically infer the task chain and interdependencies, but it does not work with Celery due to stack visibility issues for security reasons.* Defaults to False.

    ### Raises:
    
    - Exception: Only one task execution should be specified at once either lambda_task, batch_task or kubernetes_task but not two of them at the same time.
    
    - Exception: If git data is used but git is not installed.
    
    - Exception: If the configuration does not match the task description e.g. Batch with non-Batch config, etc.
    
    - Exception: If autoinfer is used with Celery.
        

    ### Returns:
    
    - Dict (from NamedTuple function definition): The components need to be specified with a NamedTuple return in the function definition, but TwinGraph converts the outputs into a Python dictionary with two components - 'hash' which includes a string indicating component hash as it was run, and 'outputs' which contains all the return values contained within the NamedTuple used in the function definition.  
    """
    
    assert callable(f_py) or f_py is None

    def _decorator(func):
        file_path = inspect.stack()[1].filename

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                parent_hash = kwargs.pop('parent_hash')
            except:
                parent_hash = []

            if type(parent_hash) == str:
                parent_hash = [parent_hash]

            if auto_infer:
                dict_of_frame = inspect.stack(context=4)[1].frame.f_locals
                context_str = (
                    ''.join((inspect.stack(context=20)[1].code_context)[2:]).strip())

                node_fcall = ast.parse(context_str[context_str.find(func.__name__):(matching_parentheses(context_str)[
                                       context_str.find(func.__name__) + len(func.__name__)]) + 1].replace('\n', '').strip().replace(' ', ''))

                depend_funcs = (list(set([(node_f) for node_f in ast.walk(node_fcall) if isinstance(
                    node_f, ast.Name) or isinstance(node_f, ast.Subscript)])))
                depend_funcs_list = [ast.unparse(
                    (depend_funcs_k)) for depend_funcs_k in depend_funcs]
                locals().update(dict_of_frame)

                for var in depend_funcs_list:
                    try:
                        parent_hash.append(eval(var + "['hash']"))
                    except Exception as e:
                        print(e)
                        pass

            parent_hash = list(set(parent_hash))

            set_randomize_time()

            component_name = str(func.__name__)

            if batch_task:
                create_component = False
                try_id=0
                max_retries=5
                while create_component == False and try_id<max_retries:
                    time.sleep(exponential_backoff(base_delay=1.2,exponent=1.5,try_id=try_id))
                    component_names = json.load(
                        open(os.path.dirname(file_path) + '/components_list_batch.json'))
                    if (component_name in component_names):
                        try:
                            print('Creating Batch component', component_name, component_names,
                                file=open(os.path.dirname(file_path) + '/log_' + str(datetime.datetime.now()) + '.txt', 'w'))
                            batch_create_component(
                                docker_id, component_name, batch_config)
                            component_names.remove(component_name)
                            json.dump(component_names, open(os.path.dirname(
                                file_path) + '/components_list_batch.json', 'w'))
                            create_component = True
                        except Exception as e:
                            #print('Try '+str(1)+' error:',e)
                            pass
                    else:
                        create_component = True
                    try_id+=1

            if lambda_task:
                create_component = False
                try_id=0
                max_retries=5
                while create_component == False and try_id<max_retries:  
                    time.sleep(exponential_backoff(base_delay=1.5,exponent=1.2,try_id=try_id))
                    component_names = json.load(open(os.path.dirname(
                        file_path) + '/components_list_lambda.json'))
                    if (component_name in component_names):
                        try:
                            print('Creating Lambda component', component_name, component_names,
                                file=open(os.path.dirname(file_path) + '/log_' + str(datetime.datetime.now()) + '.txt', 'w'))
                            lambda_create_component(
                                docker_id, component_name, lambda_config)
                            component_names.remove(component_name)
                            json.dump(component_names, open(os.path.dirname(
                                file_path) + '/components_list_lambda.json', 'w'))
                            create_component = True
                        except:
                            pass
                    else:
                        create_component = True
                    try_id+=1

            input_vals, input_dict = load_inputs(
                args=args, kwargs=kwargs, argspec=inspect.getfullargspec(func))

            child_hash = set_hash(parent_hash=parent_hash)

            gremlin_ip_port = set_gremlin_port_ip(graph_config)

            AWS_ARN = set_AWS_ARN()

            line_after_decorators = line_no(
                (inspect.getsource(func)), str(func.__name__))

            attributes = {'Name': component_name,
                          'Timestamp': str(datetime.datetime.now()),
                          'Signature': str(inspect.signature(func)),
                          'Argument Specifications': str(inspect.getfullargspec(func)),
                          'Input Values': str(input_vals),
                          'Docker Image': str(docker_id),
                          'Parent Hash': str(parent_hash),
                          'Hash': child_hash,
                          'Source Code': "\n" + "\n".join((inspect.getsource(func)).split("\n")[line_after_decorators:])
                          }
            
            if AWS_ARN != 'Unknown':
                attributes.update({'AWS ARN': AWS_ARN})

            attributes.update(additional_attributes)

            if git_data:
                import git
                with open(file_path, 'r') as git_file:
                    git_data_f = git_file.read()

                git_all_lines = git_data_f.split('\n')

                repo = git.Repo(file_path, search_parent_directories=True)
                blame = repo.git.blame(file_path).split('\n') 
                
                for i, blame_line in enumerate(blame):
                    blame[i] = blame[i].replace(git_all_lines[i], '')
                    blame[i] = (blame[i].split('(')[1]).split(')')[0]

                line_number = line_no(git_data_f, str(func.__name__))
                length_of_function = len(
                    attributes['Source Code'].split('\n'))

                relevant_blame = blame[line_number:line_number +
                                       length_of_function - 2]

                git_attributes = {'Git History': relevant_blame}
                attributes.update(git_attributes)

            poutput = namedtuple('wrap_output', ['outputs', 'hash'])

            try:
                if docker_id == 'NotProvided':
                    ioutputs = func(**input_dict)._asdict()
                    attributes.update({'Compute Platform': 'Local without Containers'})
                elif kubernetes_task:
                    ioutputs = run_kubernetes(docker_id=docker_id, input_dict=input_dict,
                                              attributes=attributes, kube_config=kube_config)._asdict()
                    attributes.update({'Compute Platform': 'Kubernetes'})
                elif batch_task:
                    ioutputs = run_aws_batch(
                        input_dict=input_dict, attributes=attributes, batch_config=batch_config)._asdict()
                    attributes.update({'Compute Platform': 'AWS Batch'})
                elif lambda_task:
                    ioutputs = run_lambda(
                        input_dict=input_dict, attributes=attributes, lambda_config=lambda_config)._asdict()
                    attributes.update({'Compute Platform': 'AWS Lambda'})
                else:
                    ioutputs = run_docker_compose(
                        docker_id=docker_id, input_dict=input_dict, attributes=attributes)._asdict()
                    attributes.update({'Compute Platform': 'Docker'})
            except:
                print('Inputs', input_dict)
                print('Attributes', attributes)
                raise Exception('Error with running function.')

            attributes.update({'Output': str(ioutputs)})
            add_vertex_connection(
                gremlin_IP=gremlin_ip_port, attributes=attributes)

            return poutput(ioutputs, child_hash)._asdict()

        return wrapper
    return _decorator(f_py) if callable(f_py) else _decorator
