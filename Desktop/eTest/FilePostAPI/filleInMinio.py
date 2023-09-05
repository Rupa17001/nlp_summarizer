import boto3
import os
class minio_client():
    def config():
         s3_client = boto3.client('s3', endpoint_url='http://127.0.0.1:9000',
                                aws_access_key_id='minioadmin',
                                aws_secret_access_key='minioadmin',
                                verify=False)
         return s3_client
    def folder_to_minio(local_folder,minio_bucket):
        print("this is minio's call ")
        #calling s3_client by making object
        s3 = minio_client.config()
        for root, dirs, files in os.walk(local_folder):
            for file in files:
                local_file_path = os.path.join(root, file)
                s3_key = os.path.relpath(local_file_path, local_folder)
                s3.upload_file(local_file_path, minio_bucket, s3_key)

    def get_minio_file_link(bucket_name, object_name):
        # Construct the MinIO file link
        minio_file_link = f"http://127.0.0.1:9000/{bucket_name}/{object_name}"
        return minio_file_link