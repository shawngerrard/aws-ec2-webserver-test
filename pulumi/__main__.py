# Import modules
import pulumi
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
import requests
import pulumi_aws as aws
# import * as k3s from "@pulumi/kubernetes";
# import pulumi_kubernetes as k3s


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

# Install Helm
# curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
# chmod 700 get_helm.sh
# ./get_helm.sh

# Install K3S
curl -sfL https://get.k3s.io | sh -s - server --no-deploy traefik --no-deploy servicelb

# Create Lit Republic namespace and context in Kubernetes
kubectl create namespace litrepublic
kubectl config set-context litrepublic-www --namespace=litrepublic --user=default --cluster=default
kubectl config use-context litrepublic-www

# Add Bitnami Helm chart repository for Nginx
# helm repo add bitnami https://charts.bitnami.com/bitnami

echo "<html><head><title>Lit Republic WWW Test</title></head><body>Well, helo thar fren!</body></html>" > /home/ubuntu/index.html
"""

# Define the NGINX Ingress Controller to be deployed through Helm
# nginx_ingress = Chart(
#     "nginx-ingress",
#     ChartOpts(
#         chart="nginx-ingress-controller",
#         version="1.24.4",
#         namespace="litrepublic",
#         fetch_opts=FetchOpts(
#             repo="https://charts.bitnami.com/bitnami",
#         ),
#     ),
# )


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

# Export the public IP and hostname of the Amazon server to output
pulumi.export('publicIp', server.public_ip)
pulumi.export('publicHostName', server.public_dns)

# STEPS
# Install Pulumi
# Create Pulumi project
# Create a virtual environment and install dependencies
    # create virtual env
        # python3 -m venv venv
    # update wheel to ensure this is built OK
        # sudo pip3 install wheel --upgrade 
    # install deps
        # venv/bin/pip install -r requirements.txt
# Modify __main__.py with deployment attributes (UserData)
# 
# Create EC2 instance
# Check if Traefik installed on instance
    # sudo kubectl get deployments -n kube-system
    # Uninstall Traefik
# ensure wheel is up to date before 