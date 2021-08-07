#!/bin/bash -xe

# log user data script execution and output to /var/log/bootstrap_trino.log
exec > >(tee /var/log/bootstrap_trino.log|logger -t user-data ) 2>&1

IS_COORDINATOR=false
IS_BOOTSTRAP=true
IS_EBS_REQUIRED=true
S3_PATH="s3://my-bucket/trino-config"
bootstrap_script="${S3_PATH}/bootstrap_trino.sh"
local_file="/opt/bootstrap_trino.sh"
aws s3 cp ${bootstrap_script} ${local_file} --no-progress
source ${local_file} "${S3_PATH}" ${IS_COORDINATOR} ${IS_BOOTSTRAP} ${IS_EBS_REQUIRED}
