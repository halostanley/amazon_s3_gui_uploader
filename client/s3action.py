import os
import boto3
from boto3.s3.transfer import S3Transfer
from boto3.s3.transfer import TransferConfig
from boto3.exceptions import S3TransferFailedError
import logging
logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] : %(message)s',
    )
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fh = logging.FileHandler("log.txt")
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s, %(name)s, [%(levelname)s] : %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

KB = 1024
MB = KB * KB
# file uplaod multipart threading
config = TransferConfig(
    multipart_threshold=8 * MB,
    max_concurrency=10,
    multipart_chunksize=8 * MB * MB,
    num_download_attempts=5,
    max_io_queue=100,
    io_chunksize=262144,
    use_threads=True)


class amazons3:

    def __init__(self, aws_access, aws_key):
        self.aws_access = aws_access
        self.aws_key = aws_key
        self.conn_test_region = 'ap-northeast-1'
        self.conn_test_bucket = 'iems5703testconnection'


    def check_client_connection(self):
        check_flag = False
        client = boto3.client(
            's3',
            aws_access_key_id = self.aws_access,
            aws_secret_access_key = self.aws_key,
            region_name = self.conn_test_region
        )

        try:
            response = client.head_bucket(Bucket=self.conn_test_bucket)
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                check_flag = True
        except:
            logger.info("Client connection error")

        return check_flag


    def buckets_list(self):
        client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access,
            aws_secret_access_key=self.aws_key,
        )
        response = client.list_buckets()
        buckets = []
        if "Buckets" in response:
            #print("There are total %d bucket(s):" % len(response['Buckets']))
            for i, bucket in enumerate(response['Buckets']):
                buckets.append(bucket['Name'])

        return buckets


    def bucket_folders_list(self, bucket):
        client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access,
            aws_secret_access_key=self.aws_key
        )
        files_list = []
        for key in client.list_objects_v2(Bucket=bucket)['Contents']:
            files_list.append(key['Key'])

        return files_list


    def dir_list(self, path):
        files_path = []
        for root, dirs, files in os.walk(path):
            for file in files:
                key_path = os.path.join(root, file)
                if ".DS_Store" not in key_path:
                    key_path = key_path.replace("./", "", 1)
                    files_path.append(key_path)

        return files_path


    def upload_single_file(self, path, key, bucket): #using this method now.
        client = boto3.client(
            's3',
            aws_access_key_id = self.aws_access,
            aws_secret_access_key = self.aws_key,
        )
        transfer = S3Transfer(client, config)
        success_flag = True
        try:
            transfer.upload_file(filename=path,
                                 bucket=bucket,
                                 key=key)
        except S3TransferFailedError as err:
            logger.info("S3TransferFailedError: {}".format(key))
            success_flag = False

        finally:
            return success_flag


    def get_key_url(self, bucket, key):
        client = boto3.client(
            's3',
            aws_access_key_id = self.aws_access,
            aws_secret_access_key = self.aws_key,
        )
        download_url = client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': str(key)
            },
            HttpMethod='GET',
            #expires 30 days
            ExpiresIn='2592000'
        )

        return download_url