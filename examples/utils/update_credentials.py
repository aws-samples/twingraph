import os
import boto3


def get_account_id():
    client = boto3.client("sts")
    return client.get_caller_identity()["Account"]


def get_default_region():
    my_session = boto3.session.Session()
    return my_session.region_name


# Replace the following
account_id = get_account_id()
region_id = get_default_region()


def replace_string(action, original_str, replaced_str, directory):
    for dname, dirs, files in os.walk(directory):
        for fname in files:
            folder_name = dname.split('/')[-1]
            if ('.py' in fname or '.json' in fname) and folder_name != 'utils' and folder_name != '__pycache__' and fname != '__init__.py':
                print(action, 'id in', dname, fname)
                fpath = os.path.join(dname, fname)
                with open(fpath) as f:
                    s = f.read()
                s = s.replace(original_str, replaced_str)
                with open(fpath, "w") as f:
                    f.write(s)


replace_string('Updated account', '<AWS-ACCOUNT-ID>',
               str(account_id), '../orchestration_demos/')
replace_string('Updated region', '<AWS-REGION-ID>',
               str(region_id), '../orchestration_demos/')

replace_string('Updated account', '<AWS-ACCOUNT-ID>',
               str(account_id), '../../tests/')
replace_string('Updated region', '<AWS-REGION-ID>',
               str(region_id), '../../tests/')
