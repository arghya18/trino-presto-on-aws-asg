from cluster import config
import boto3

client = boto3.client('autoscaling', region_name=config.region)
response = client.create_auto_scaling_group(
    AutoScalingGroupName=config.asg_name,
    LaunchTemplate={
        # 'LaunchTemplateId': 'string',
        'LaunchTemplateName': config.launch_template_name,
        'Version': '$Default'
    },
    MinSize=0,
    MaxSize=1,
    DesiredCapacity=0,
    DefaultCooldown=300,
    AvailabilityZones=[config.availability_zone],
    LoadBalancerNames=[],
    TargetGroupARNs=[],
    HealthCheckType='EC2',
    HealthCheckGracePeriod=300,
    # PlacementGroup='string',
    VPCZoneIdentifier=config.subnet_id,
    TerminationPolicies=['OldestInstance'],
    NewInstancesProtectedFromScaleIn=True if config.setup_coordinator else False,
    LifecycleHookSpecificationList=[
        {
            'LifecycleHookName': 'shutdown-hook',
            'LifecycleTransition': 'autoscaling:EC2_INSTANCE_TERMINATING',
            'NotificationMetadata': config.worker_port,
            'HeartbeatTimeout': config.scale_down_timeout,
            'DefaultResult': 'ABANDON'
        },
    ] if config.setup_coordinator else [
        {
            'LifecycleHookName': 'shutdown-hook',
            'LifecycleTransition': 'autoscaling:EC2_INSTANCE_TERMINATING',
            'NotificationMetadata': config.worker_port,
            'HeartbeatTimeout': config.scale_down_timeout,
            'DefaultResult': 'ABANDON',
            'NotificationTargetARN': config.sqs_arn,
            'RoleARN': config.sqs_role_arn
        }
    ]
)

print(response)
