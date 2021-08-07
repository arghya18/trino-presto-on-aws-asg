import base64
import fileinput
import re

# ========= Define configs ==========

setup_coordinator = False

# generic configs
region = 'us-east-1'
availability_zone = 'us-east-1a'
security_group_id = 'sg-xxxx'
subnet_id = 'subnet-xxxx'


# ========= launch template configs =========
launch_template_coordinator = 'trino-coordinator-lt'
launch_template_worker_od = 'trino-worker-spot-lt'
launch_template_name = launch_template_coordinator if setup_coordinator else launch_template_worker_od
ami_image_id = 'ami-xxxxxxxxxxx'
instance_type = 'r4.8xlarge'
ebs_size_gb = 1024
is_ebs_required = True if ebs_size_gb != 0 else False
is_spot = True if 'spot' in launch_template_name else False
ssh_key_name = 'key.ppk'
ec2_iam_name = ‘Trino_IAM_Role’
monitoring = False

bootstrap_file = 'bootstrap_wrapper.sh'
with fileinput.FileInput('bootstrap_wrapper.sh', inplace=True) as file:
    for line in file:
        line = re.sub('IS_COORDINATOR=.*$', 'IS_COORDINATOR=' + str(setup_coordinator).lower(), line)
        line = re.sub('IS_EBS_REQUIRED=.*$', 'IS_EBS_REQUIRED=' + str(is_ebs_required).lower(), line)
        print(line, end='')

with open(bootstrap_file, 'rb') as input_file:
    user_data = base64.b64encode(input_file.read()).decode("utf-8")


# ========= auto scaling group configs =========

asg_name_coordinator = 'trino-coordinator-asg'
asg_name_worker_od = 'trino-worker-spot-asg'

if setup_coordinator:
    asg_name = asg_name_coordinator
    scale_down_timeout = 7200
else:
    asg_name = asg_name_worker_od
    scale_down_timeout = 7200

worker_port = '8080'    # Change if required


# ========= sqs configs =========
sqs_prefix = 'arn:aws:sqs:us-east-1:088888888888:'
sqs_name = 'trino-scale-down-sqs'
sqs_arn = sqs_prefix + sqs_name
sqs_role_arn = 'arn:aws:iam::088888888888:role/Trino_NotificationRole'


# ========= lambda configs =========
lambda_function_name = 'trino-scale-down-lambda'
lambda_role_arn = 'arn:aws:iam::088888888888:role/lambda-role'


# ========= cron configs =========
with fileinput.FileInput('shutdown_cron.sh', inplace=True) as file:
    for line in file:
        line = re.sub('region_name=.*$', "region_name='" + region + "'", line)
        print(line, end='')
