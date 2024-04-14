# Before we start , Make sure you notice down your S3 access key and S3 secret Key.
# 1. AWS Configure
#
# Before we could work with AWS S3. We need to configure it first.
#
#     Install awscli using pip
#
# pip install awscli
#
#     Configure
#
# aws configure
# AWS Access Key ID [None]: input your access key
# AWS Secret Access Key [None]: input your secret access key
# Default region name [None]: input your region
# Default output format [None]: json
#
#     Verifies
#
# aws s3 ls
#
# if you see there is your bucket show up. it mean your configure is correct. Ok, Now let's start with upload file.


import boto3
import os


db_name = ""
new_db_name='' # only In case if you  want to duplicate the old db data to new one

bucket_name = ""

os.environ['AWS_ACCESS_KEY_ID'] = "XXXXXXXXXXXXXXX"
os.environ['AWS_SECRET_ACCESS_KEY'] = "XXXXXXXXXXXXXXXXXXXX"
region = 'ap-south-1'

# odoo file store path
local_file = "/root/.local/share/Odoo/filestore/"

# s3 client object
s3_client = boto3.client('s3',region_name=region)


def download_dir(prefix, local, bucket, client):
    """
        params:
        - prefix: pattern to match in s3
        - local: local path to folder in which to place files
        - bucket: s3 bucket with target contents
        - client: initialized s3 client object
    """


    keys = []
    dirs = []
    next_token = ''
    base_kwargs = {
        'Bucket': bucket,
        'Prefix': prefix,
    }
    while next_token is not None:
        kwargs = base_kwargs.copy()
        if next_token != '':
            kwargs.update({'ContinuationToken': next_token})
        results = client.list_objects_v2(**kwargs)
        contents = results.get('Contents')
        for i in contents:
            k = i.get('Key')
            if k[-1] != '/':
                keys.append(k)
            else:
                dirs.append(k)
        next_token = results.get('NextContinuationToken')
    for d in dirs:
        dest_pathname = os.path.join(local, d)
        if new_db_name:
            dest_pathname =dest_pathname.replace(prefix,new_db_name)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
    for k in keys:
        dest_pathname = os.path.join(local, k)
        if new_db_name:
            dest_pathname=dest_pathname.replace(prefix,new_db_name)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
        client.download_file(bucket, k, dest_pathname)
        if new_db_name:
            print (f'{k} Moved Into {dest_pathname}')
        else:
            print(k)
    print ("=======Finish Download========")


download_dir(db_name, local_file, bucket_name, s3_client)
