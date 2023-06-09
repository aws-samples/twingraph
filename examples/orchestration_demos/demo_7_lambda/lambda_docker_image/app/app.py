import os
def handler(event, context):
    response = exec(event['python_str'])
    print('CLOUDWATCHER',os.environ['AWS_LAMBDA_LOG_STREAM_NAME'],event['hash'],'OBTAINED_CLOUDWATCHER')
    return response