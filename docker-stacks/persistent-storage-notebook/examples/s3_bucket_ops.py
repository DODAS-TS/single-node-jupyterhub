from boto3sts import credentials as creds
import boto3

# Get your refreshble credentials session with the oidc-agent profile named e.g.: dodas_oidc-agen-profile
aws_session = creds.assumed_session("dodas_oidc-agen-profile")

# Use the generated session for all the data operations on an s3 bucket
s3 = aws_session.client('s3', endpoint_url="https://minio.cloud.infn.it/", config=boto3.session.Config(signature_version='s3v4'),
                                                verify=True)
for key in s3.list_objects(Bucket='ciangottini')['Contents']:
        print(key['Key'])
