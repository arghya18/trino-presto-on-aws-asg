#!/usr/bin/env bash

presto_running=$(pgrep "presto-server"| wc -l)

if [[ ${presto_running} == 0 ]]; then
    echo "Presto is not running, sending complete lifecycle action"
    region_name='us-east-1'
    ec2_instance_id=$(curl http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null)
    asg_name=$(aws autoscaling describe-auto-scaling-instances --instance-ids=${ec2_instance_id} --region ${region_name} \
    --query AutoScalingInstances[0].AutoScalingGroupName --output text)

    aws autoscaling complete-lifecycle-action --lifecycle-action-result CONTINUE --instance-id ${ec2_instance_id} \
    --lifecycle-hook-name shutdown-hook --auto-scaling-group-name ${asg_name} --region ${region_name}
fi
