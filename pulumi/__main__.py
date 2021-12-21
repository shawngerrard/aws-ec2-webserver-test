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
admin_group = aws.ec2.SecurityGroup('litrepublicpoc-administrator-secg',
    description='Enable SSH and HTTP access for Lit Republic',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': [extip.text.strip()+'/32'] },
        { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0'] },
        { 'protocol': 'tcp', 'from_port': 443, 'to_port': 443, 'cidr_blocks': ['0.0.0.0/0'] },
        { 'protocol': 'tcp', 'from_port': 6443, 'to_port': 6443, 'cidr_blocks': [extip.text.strip()+'/32'] }
    ],
    egress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': [extip.text.strip()+'/32'] },
        { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0'] },
        { 'protocol': 'tcp', 'from_port': 443, 'to_port': 443, 'cidr_blocks': ['0.0.0.0/0'] },
        { 'protocol': 'tcp', 'from_port': 6443, 'to_port': 6443, 'cidr_blocks': [extip.text.strip()+'/32'] }
    ])

# Define the instance start-up scripting for the master server
server_master_user_data = """#!/bin/bash

# Install Helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# Install K3S
curl -sfL https://get.k3s.io | sh -s - server --write-kubeconfig-mode 644 --no-deploy traefik --no-deploy servicelb

# Create Lit Republic namespace and context in Kubernetes
kubectl create namespace litrepublic
kubectl config set-context litrepublic-www-dev --namespace=litrepublic --user=default --cluster=default
kubectl config use-context litrepublic-www-dev

echo "<html><head><title>Lit Republic WWW Test - Master</title></head><body><p>Well, helo thar fren!</p><p>From Master</p></body></html>" > /home/ubuntu/index.html
"""

# # Define the instance start-up scripting for the first worker
# worker1_user_data = """#!/bin/bash

# # Install K3S
# curl -sfL https://get.k3s.io | sh -s - server --write-kubeconfig-mode 644 --no-deploy traefik --no-deploy servicelb

# echo "<html><head><title>Lit Republic WWW Test - Worker 1</title></head><body><p>Well, helo thar fren!</p><p>From Worker 1</p></body></html>" > /home/ubuntu/index.html
# """

# # Define the instance start-up scripting for the second worker
# worker2_user_data = """#!/bin/bash

# # Install K3S
# curl -sfL https://get.k3s.io | sh -s - server --write-kubeconfig-mode 644 --no-deploy traefik --no-deploy servicelb

# echo "<html><head><title>Lit Republic WWW Test - Worker 2</title></head><body><p>Well, helo thar fren!</p><p>From Worker 2</p></body></html>" > /home/ubuntu/index.html
# """

# Define our master node as an AWS EC2 instance
server_master = aws.ec2.Instance('litrepublicpoc-www-dev-master',
    instance_type=size,
    vpc_security_group_ids=[admin_group.id], 
    user_data=server_master_user_data,
    ami=ami.id,
    key_name='LitRepublicPoc',
    tags={
        "Name":"litrepublicpoc-ec2-master"
    })

# # Define our worker node as an AWS EC2 instance
# worker_1 = aws.ec2.Instance('litrepublicpoc-www-dev-worker1',
#     instance_type=size,
#     vpc_security_group_ids=[admin_group.id], 
#     user_data=worker1_user_data,
#     ami=ami.id,
#     key_name='LitRepublicPoc',
#     tags={
#         "Name":"litrepublicpoc-ec2-worker1"
#     })

# # Define another worker node as an AWS EC2 instance
# worker_2 = aws.ec2.Instance('litrepublicpoc-www-dev-worker2',
#     instance_type=size,
#     vpc_security_group_ids=[admin_group.id], 
#     user_data=worker2_user_data,
#     ami=ami.id,
#     key_name='LitRepublicPoc',
#     tags={
#         "Name":"litrepublicpoc-ec2-worker2"
#     })

# Obtain the private key to use
key = open('/home/shawn/.ssh/LitRepublicPoc.pem', "r")

# Configure provisioner connection string to master node
conn_master = provisioners.ConnectionArgs(
    host=server_master.public_ip,
    username='ubuntu',
    private_key=key.read()
)

# TODO: Implement Py FOR loop to check if K3S service and Helm have installed and are running before doing stuff
# Is there a Pulumi native way to achieve this?

# Execute commands to configure the master node using the provisioner module
server_master_config = provisioners.RemoteExec('server_master_config',
    conn=conn_master,
    opts=pulumi.ResourceOptions(depends_on=[server_master]),
    commands=[
        'sleep 7s',
        'helm repo add bitnami https://charts.bitnami.com/bitnami',
        'mkdir -p ~/.kube',
        'sleep 10s',
        'ls -la /etc/rancher/k3s',
        'cp /etc/rancher/k3s/k3s.yaml ~/.kube/config',
        'helm install litrepublicpoc-ec2-nginx bitnami/nginx-ingress-controller',
        'export TEST="Leshhh Gooooo!"',
        'sleep 10s'
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
# Run Pulumi Up
# SSH
    # verify installation
# SCP kubeconfig file from ec2 to local
    # update kubeconfig file with external ip of ec2
# install kubectl
# verifying kubectl install
    # remove TLS certificate check from node
        # kubectl --version
        # kubectl get nodes --insecure-skip-tls-verify
# Deploy wordpress
    # Use 'set' option in helm install to configure wordpress