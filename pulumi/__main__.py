# Import modules
import pulumi
import requests
import pulumi_aws as aws

# Set variable constants
size = 't2.micro'
extip = requests.get('http://checkip.amazonaws.com/')

# Define Amazon Machine Image to use
ami = aws.ec2.get_ami(most_recent="true",
                  owners=["099720109477"],
                  filters=[{"name":"image-id","values":["ami-0bf8b986de7e3c7ce"]}])

# Define administrator security group to allow SSH & HTTP access
group = aws.ec2.SecurityGroup('administrator-sg-litrepublicpoc',
    description='Enable SSH and HTTP access for Lit Republic',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': [extip.text.strip()+'/32'] },
        { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0'] },
        { 'protocol': 'tcp', 'from_port': 443, 'to_port': 443, 'cidr_blocks': ['0.0.0.0/0'] }
    ],
    egress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': [extip.text.strip()+'/32'] },
        { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0'] },
        { 'protocol': 'tcp', 'from_port': 443, 'to_port': 443, 'cidr_blocks': ['0.0.0.0/0'] }
    ])

# Define the instance start-up scripting
user_data = """#!/bin/bash

# Install K3S
curl -sfL https://get.k3s.io | sh -

# Install Helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami

echo "<html><head><title>Lit Republic WWW Test</title></head><body>Well, helo thar fren!</body></html>" > /home/ubuntu/index.html
"""

# Define the AWS EC2 instance to start
server = aws.ec2.Instance('litrepublicpoc-www',
    instance_type=size,
    vpc_security_group_ids=[group.id], 
    user_data=user_data,
    ami=ami.id,
    key_name='LitRepublicPoc',
    tags={
        "Name":"litrepublicpoc-ec2"
    })
    
# Current connection string:
# ssh -i ~/.ssh/LitRepublicPoc.pem ubuntu@`aws ec2 describe-instances --filters Name=instance-state-name,Values=running Name=tag:Name,Values=litrepublicpoc-ec2 --query 'Reservations[].Instances[].PublicDnsName' --output text`

# Export the public IP and hostname of the Amazon server
pulumi.export('publicIp', server.public_ip)
pulumi.export('publicHostName', server.public_dns)