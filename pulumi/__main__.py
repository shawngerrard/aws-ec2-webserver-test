# Import modules
import pulumi
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
#from pulumi_kubernetes.apps.v1 import Deployment
import requests
import pulumi_aws as aws
import pulumi_kubernetes as k3s
import provisioners

# Attach a label to the application for easy identification/querying
#app_labels = { "app": "nginx" }

# # Define a Kubernetes NGINX deployment
# deployment = k3s.apps.v1.Deployment(
#      "nginx",
#      spec={
#          "selector": { "match_labels": app_labels },
#          "replicas": 1,
#          "template": {
#              "metadata": { "labels": app_labels },
#              "spec": { "containers": [{ "name": "nginx", "image": "nginx" }] }
#          }
#      })

# Set variable constants
size = 't3.micro'
extip = requests.get('http://checkip.amazonaws.com/')

# Define Amazon Machine Image to use
ami = aws.ec2.get_ami(most_recent="true",
                  owners=["099720109477"],
                  filters=[{"name":"image-id","values":["ami-0bf8b986de7e3c7ce"]}])

# Define administrator security group to allow SSH & HTTP access
group = aws.ec2.SecurityGroup('litrepublicpoc-administrator-secg',
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
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# Install K3S
curl -sfL https://get.k3s.io | sh -s - server_master --no-deploy traefik --no-deploy servicelb

# Create Lit Republic namespace and context in Kubernetes
kubectl create namespace litrepublic
kubectl config set-context litrepublic-www --namespace=litrepublic --user=default --cluster=default
kubectl config use-context litrepublic-www

echo "<html><head><title>Lit Republic WWW Test</title></head><body>Well, helo thar fren!</body></html>" > /home/ubuntu/index.html
"""

# Define the AWS EC2 instance to start
server_master = aws.ec2.Instance('litrepublicpoc-www-dev-controller',
    server_master_type=size,
    vpc_security_group_ids=[group.id], 
    user_data=user_data,
    ami=ami.id,
    key_name='LitRepublicPoc',
    tags={
        "Name":"litrepublicpoc-ec2-master"
    })

key = open('/home/shawn/.ssh/LitRepublicPoc.pem', "r")

conn = provisioners.ConnectionArgs(
    host=server_master.public_ip,
    username='ubuntu',
    private_key=key.read()
)

# Execute the commands on the new instance
cat_config = provisioners.RemoteExec('cat-config',
    conn=conn,
    commands=[
        'sleep 7s',
        'helm repo add bitnami https://charts.bitnami.com/bitnami',
        'echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.bashrc && . ~/.bashrc'
    ]
)

# Current connection string:
# ssh -i ~/.ssh/LitRepublicPoc.pem ubuntu@`aws ec2 describe-instances --filters Name=instance-state-name,Values=running Name=tag:Name,Values=litrepublicpoc-ec2 --query 'Reservations[].Instances[].PublicDnsName' --output text`

# Export the public IP and hostname of the Amazon server to output
pulumi.export('publicIp', server_master.public_ip)
pulumi.export('publicHostName', server_master.public_dns)

# Define the NGINX Ingress Controller to be deployed through Helm
# Note: No longer needed due to remote execution of Helm repository?
# nginx_ingress = Chart(
#     "nginx-ingress",
#     ChartOpts(
#         chart="nginx-ingress-controller",
#         version="9.0.9",
#         namespace="litrepublic",
#         fetch_opts=FetchOpts(
#             repo="https://charts.bitnami.com/bitnami",
#         ),
#     ),
# )

# Output the deployment name
# pulumi.export("name", deployment.metadata["name"])


#-------
# STEPS
#-------
# Install Pulumi
# Install dependencies for the Provisioner module
    # Install paramiko
        # pip install paramiko
    # Install typing_extensions
        # pip install typing_extensions
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