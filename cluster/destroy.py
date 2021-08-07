from cluster import config
import boto3

# Destroy Cluster
print('==== Destroying Cluster ====\n\n')
exit(0)

# Destroy Lambda with Event Source Mapping
print('==== Destroying Lambda with Event Source Mapping=====\n')
client = boto3.client('lambda')
event_source = client.list_event_source_mappings(FunctionName=config.lambda_function_name)
uuid = event_source['EventSourceMappings'][0]['UUID']
print(uuid)

event_source_response = client.delete_event_source_mapping(UUID=uuid)
print(event_source_response)

lambda_response = client.delete_function(FunctionName=config.lambda_function_name)
print(lambda_response)

# Destroy SQS
print('==== Destroying SQS ====\n')
client = boto3.client('sqs')
queue_url_response = client.get_queue_url(QueueName=config.sqs_name)
print(queue_url_response['QueueUrl'])

sqs_response = client.delete_queue(QueueUrl=queue_url_response['QueueUrl'])
print(sqs_response)

# Destroy ASGs
print('==== Destroying auto scaling group =====\n')
client = boto3.client('autoscaling')
asg_worker_response = client.delete_auto_scaling_group(AutoScalingGroupName=config.asg_name_worker_od, ForceDelete=False)
print(asg_worker_response)

asg_coordinator_response = client.delete_auto_scaling_group(AutoScalingGroupName=config.asg_name_coordinator, ForceDelete=False)
print(asg_coordinator_response)

# Destroy Launch Templates
print('==== Destroying launch template =====\n\n')
client = boto3.client('ec2')
lt_worker_od_response = client.delete_launch_template(LaunchTemplateName=config.launch_template_worker_od)
print(lt_worker_od_response)

lt_coordinator_response = client.delete_launch_template(LaunchTemplateName=config.launch_template_coordinator)
print(lt_coordinator_response)

print('============== Cluster Destroyed Completed unless any error reported above ==============')
