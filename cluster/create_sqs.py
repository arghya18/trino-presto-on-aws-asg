from cluster import config
import boto3
import json


client = boto3.client('sqs', region_name=config.region)
response = client.create_queue(
    QueueName=config.sqs_name,
    Attributes={
        'VisibilityTimeout': '30',
        'MessageRetentionPeriod': '1800'
    }
)
print(response)
queue_url = response['QueueUrl']
account_id = queue_url.split('/')[3]

response = client.tag_queue(
    QueueUrl=queue_url,
    Tags={
        'AppName': config.tag_app_name
    }
)
print(response)

response = client.add_permission(
    QueueUrl=queue_url,
    Label='HookLambda',
    AWSAccountIds=[account_id],
    Actions=['DeleteMessage', 'SendMessage', 'ReceiveMessage', 'ListDeadLetterSourceQueues', 'ChangeMessageVisibility',
             'GetQueueAttributes', 'GetQueueUrl']
)
print(response)

sqs = boto3.resource('sqs')
queue = sqs.create_queue(QueueName=config.sqs_name)
policy = json.loads(queue.attributes['Policy'])
new_policy = policy
new_policy['Statement'][0]['Principal'] = '*'
queue.set_attributes(Attributes={'Policy': json.dumps(new_policy)})
