from cluster import config
import boto3


ec2 = boto3.client('ec2', region_name=config.region)
response = ec2.create_launch_template(
    DryRun=False,
    LaunchTemplateName=config.launch_template_name,
    VersionDescription='PRD',
    LaunchTemplateData={
        'EbsOptimized': True,
        'IamInstanceProfile': {
            'Name': config.ec2_iam_name
        },
        'BlockDeviceMappings': [
            {
                'DeviceName': '/dev/xvdb',
                'Ebs': {
                    'Encrypted': False,
                    'DeleteOnTermination': True,
                    'VolumeSize': config.ebs_size_gb,
                    'VolumeType': 'st1'
                },
            },
        ] if config.is_ebs_required else [],
        'ImageId': config.ami_image_id,
        'InstanceType': config.instance_type,
        'KeyName': config.ssh_key_name,
        'Monitoring': {
            'Enabled': config.monitoring
        },
        'DisableApiTermination': False if config.is_spot else True,
        'InstanceInitiatedShutdownBehavior': 'terminate' if config.is_spot else 'stop',
        'InstanceMarketOptions': {'MarketType': 'spot'} if config.is_spot else {},
        'UserData': config.user_data,
        'SecurityGroupIds': [config.security_group_id]
    }
)

print(response)
