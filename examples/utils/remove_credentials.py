import os
import boto3
from update_credentials import replace_string


def get_account_id():
    client = boto3.client("sts")
    return client.get_caller_identity()["Account"]


def get_default_region():
    my_session = boto3.session.Session()
    return my_session.region_name


# Replace the following
account_id = get_account_id()
region_id = get_default_region()

replace_string('Removed account', str(account_id), '<AWS-ACCOUNT-ID>',
               '../orchestration_demos/')

replace_string('Removed region', str(region_id), '<AWS-REGION-ID>',
               '../orchestration_demos/')

replace_string('Removed account', str(account_id), '<AWS-ACCOUNT-ID>',
               '../../tests/')

replace_string('Removed region', str(region_id), '<AWS-REGION-ID>',
               '../../tests/')