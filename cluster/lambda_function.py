from botocore.vendored import requests
import boto3
import json


def initiate_presto_shutdown(nodes, port):
    successful_nodes = list()
    for node in nodes:
        url = 'http://{0}:{1}/v1/info/state'.format(node, port)
        print(url)
        header = {'Content-Type': 'application/json'}
        try:
            response = requests.put(url, data='"SHUTTING_DOWN"', headers=header, timeout=25)
        except Exception as e:
            print('Error: {}'.format(str(e)))
            raise e
        else:
            print('Shut down request sent successfully for: {}'.format(node))
            successful_nodes.append(node)
        print(response.text)
        print(response.status_code)
    return successful_nodes


def lambda_handler(event, context):
    print(event)

    try:
        event_body = json.loads(event['Records'][0]['body'])
        transition = event_body['LifecycleTransition']
        instance_id = event_body['EC2InstanceId']
        worker_port = event_body['NotificationMetadata']
        print('LifecycleTransition: {}, EC2InstanceId: {}, WorkerPort: {}'.format(transition, instance_id, worker_port))

        if transition != 'autoscaling:EC2_INSTANCE_TERMINATING':
            print('Not a termination event')
            return
    except Exception as e:
        print(str(e))
        print('Not a valid event')
    else:
        print('Getting ip address from ec2 instance id')
        private_ip = boto3.resource('ec2').Instance(instance_id).private_ip_address
        print('Private IP: {}'.format(private_ip))
        initiate_presto_shutdown([private_ip], worker_port)
