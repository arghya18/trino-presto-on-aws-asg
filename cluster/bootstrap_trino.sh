#!/bin/bash -xe

TMP_DIR=$(mktemp -d)
WORKERS_DIR="${TMP_DIR}/config/workers"
CATALOGS_DIR="${TMP_DIR}/config/catalog"
COORDINATOR_DIR="${TMP_DIR}/config/coordinator"
COMMON_DIR="${TMP_DIR}/config/common"
S3_PATH="${1}"
IS_COORDINATOR=${2}
IS_BOOTSTRAP=${3}
IS_EBS_REQUIRED=${4}

# download workers configuration
aws s3 cp "${S3_PATH}/trino-config.zip" /tmp/ --no-progress
unzip /tmp/trino-config.zip -d ${TMP_DIR}

# setup catalog configuration
cp -rv ${CATALOGS_DIR} /etc/trino/

# setup common properties
cp -rv ${COMMON_DIR}/* /etc/trino/

# setup other configuration
if [[ ${IS_COORDINATOR} == true ]]; then
    cp -rv ${COORDINATOR_DIR}/* /etc/trino/
    local_hostname=$(curl http://169.254.169.254/latest/meta-data/local-ipv4 2>/dev/null)
    sed -i "s/LOCAL_HOSTNAME/${local_hostname}/g" /etc/trino/config.properties
else
    cp -rv ${WORKERS_DIR}/* /etc/trino/
    coordinator_ip=$(aws ec2 describe-instances --instance-ids $(aws autoscaling describe-auto-scaling-instances --region us-east-1 --query 'AutoScalingInstances[?AutoScalingGroupName==`trino-coordinator-asg`]'.InstanceId --output text) --region us-east-1 --query Reservations[].Instances[].PrivateIpAddress --output text)
    sed -i "s/COORDINATOR_IP/${coordinator_ip}/g" /etc/trino/config.properties
fi

# exit after config changes
if [[ ${IS_BOOTSTRAP} == false ]]; then
    echo "Changes deployed successfully"
    exit 0
fi

# modify node.properties
sed -i "/node.environment=/ s|=.*|=prod|g" /etc/trino/node.properties
uuid=$(uuidgen)
sed -i "/node.id=/ s|=.*|=${uuid}|g" /etc/trino/node.properties

# setup udf
aws s3 cp "${S3_PATH}/plugin/udf" /usr/lib/trino/plugin/udf/ --recursive --no-progress

# mount EBS on ec2 nodes and setup spill paths
if [[ ${IS_EBS_REQUIRED} == true && ${IS_COORDINATOR} == false ]]; then
    IDX=1
    for DEV in /dev/disk/by-id/nvme-Amazon_EC2_NVMe_Instance_Storage_*-ns-1; do  mkfs.xfs ${DEV};mkdir -p /mnt${IDX};echo ${DEV} /mnt${IDX} xfs defaults,noatime 1 2 >> /etc/fstab; IDX=$((${IDX} + 1)); done
    mount -a
fi

mkdir -p /mnt1/rubix
mkdir -p /mnt2/rubix
mkdir -p /mnt1/spill
mkdir -p /mnt2/spill
chmod -R 777 /mnt1
chmod -R 777 /mnt2

# start trino service
systemctl enable trino
systemctl start trino

# setup shutdown cron
if [[ ${IS_COORDINATOR} == false ]]; then
    aws s3 cp "${S3_PATH}/shutdown_cron.sh" "/opt/shutdown_cron.sh" --no-progress
    chmod +x "/opt/shutdown_cron.sh"
    echo "*/2 * * * * /opt/shutdown_cron.sh > /var/log/shutdown_cron.log 2>&1" >> "/var/spool/cron/root"
else
    wget -O /home/ec2-user/trino https://repo1.maven.org/maven2/io/trino/trino-cli/359/trino-cli-359-executable.jar
    chmod 777 /home/ec2-user/trino    
fi
