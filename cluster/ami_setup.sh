#!/usr/bin/env bash

#login as root
sudo su

trino_version="359"

# install java 11
yum install java-11-amazon-corretto -y
java -version

# change limits
echo -e "fs.file-max = 1000001" >> /etc/sysctl.conf

echo -e "* hard nofile 1000000" >> /etc/security/limits.conf
echo -e "* soft nofile 1000000" >> /etc/security/limits.conf
echo -e "* hard nproc 1000000" >> /etc/security/limits.conf
echo -e "* soft nproc 1000000" >> /etc/security/limits.conf

echo -e "* hard nofile 1000000" >> /etc/security/limits.d/20-nproc.conf
echo -e "* soft nofile 1000000" >> /etc/security/limits.d/20-nproc.conf
echo -e "* hard nproc 1000000" >> /etc/security/limits.d/20-nproc.conf
echo -e "* soft noproc 1000000" >> /etc/security/limits.d/20-nproc.conf
# sed -i '/soft.*nproc/ s/4096/1000000/g' /etc/security/limits.d/20-nproc.conf

# log off and login and validate new limits
ulimit -a

# download and install presto
wget https://repo1.maven.org/maven2/io/trino/trino-server-rpm/${trino_version}/trino-server-rpm-${trino_version}.rpm
wget https://repo1.maven.org/maven2/io/trino/trino-server-rpm/${trino_version}/trino-server-rpm-${trino_version}.rpm.md5

if [[ `md5sum trino-server-rpm-${trino_version}.rpm|awk '{print $1}'` == `cat trino-server-rpm-${trino_version}.rpm.md5` ]]; then echo "GOOD"; else echo "BAD"; fi
# check the md5 manually and install if match

rpm -iv trino-server-rpm-${trino_version}.rpm

rm -f trino-server-rpm-${trino_version}.rpm
rm -f trino-server-rpm-${trino_version}.rpm.md5


# Optional
echo alias trino="'./trino --server localhost:8080 --catalog hive --schema default'" >> /home/ec2-user/.bash_profile
echo alias slog="'tail -50 /var/log/trino/server.log'" >> /home/ec2-user/.bash_profile
echo alias slogf="'tail -50f /var/log/trino/server.log'" >> /home/ec2-user/.bash_profile
echo alias log="'cd /var/log/trino'" >> /home/ec2-user/.bash_profile
echo alias conf="'cd /etc/trino'" >> /home/ec2-user/.bash_profile
