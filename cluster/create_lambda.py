from cluster import config
import zipfile
import boto3

zipfile.ZipFile('lambda_function.zip', mode='w').write("lambda_function.py")

client = boto3.client('lambda')
response = client.create_function(
    FunctionName=config.lambda_function_name,
    Runtime='python3.6',
    Role=config.lambda_role_arn,
    Handler='lambda_function.lambda_handler',
    Code={
        'ZipFile': open('lambda_function.zip', 'rb').read(),
    },
    Description='Lambda to handle scale down',
    Timeout=30,
    MemorySize=128,
    # Publish=True|False,
    VpcConfig={
        'SubnetIds': [config.subnet_id],
        'SecurityGroupIds': [config.security_group_id]
    },
    TracingConfig={'Mode': 'PassThrough'},
    Tags={'AppName': config.tag_app_name}
)
print(response)


response = client.create_event_source_mapping(
    EventSourceArn=config.sqs_arn,
    FunctionName=config.lambda_function_name,
    Enabled=True,
    BatchSize=1,
)
print(response)
