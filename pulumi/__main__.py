#----------------------------------------------------------------------------------------------------------------------
# GENERAL DEFINITIONS
#----------------------------------------------------------------------------------------------------------------------


# Import modules
import pulumi
import requests
import pulumi_aws as aws
import pulumi_command as command

# Set variable constants
size = 't3.micro'
extip = requests.get('http://checkip.amazonaws.com/')

# TODO: Implement commands to use refreshed sets of SSH keys to keep these unique
# const keyName = config.get("keyName") ?? new aws.ec2.KeyPair("key", { publicKey: config.require("publicKey") }).keyName;

# Obtain the key to use
keyfile = open('/home/shawn/.ssh/LitRepublicPoc.pem', "r")
key = keyfile.read()
keyfile.close()

# Define Amazon Machine Image (AMI) to use
ami = aws.ec2.get_ami(most_recent="true",
    owners=["099720109477"],
    filters=[{"name":"image-id","values":["ami-0bf8b986de7e3c7ce"]}],
)

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
    ],
)


#----------------------------------------------------------------------------------------------------------------------
# MASTER NODE DEFINITIONS
#----------------------------------------------------------------------------------------------------------------------


# Define the instance start-up scripting
server_master_userdata = """#!/bin/bash

# Update hostname
hostname="litrepublic-www-dev-master"
echo $hostname | tee /etc/hostname
sed -i '1s/.*/$hostname/' /etc/hosts
hostname $hostname

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

echo "<html><head><title>Lit Republic WWW - Development - Master</title></head><body>Well, helo thar fren!</body></html>" > /home/ubuntu/index.html
"""

# Define our master node as an AWS EC2 instance
server_master = aws.ec2.Instance('litrepublicpoc-www-dev-master',
    instance_type=size,
    vpc_security_group_ids=[admin_group.id], 
    user_data=server_master_userdata,
    ami=ami.id,
    key_name='LitRepublicPoc',
    tags={
        "Name":"litrepublicpoc-ec2-master"
    },
)

# Configure provisioner connection string to master node
connection_master = command.remote.ConnectionArgs(
    host=server_master.public_ip,
    user='ubuntu',
    private_key=key,
)

# TODO: Implement Py FOR loop to check if K3S service and Helm have installed and are running before doing stuff
# Is there a Pulumi native way to achieve this?

# Add the Bitnami repo to Helm
server_master_add_bitnami = command.remote.Command('master_add_bitnami',
    connection=connection_master,
    create='sleep 30 && helm repo add bitnami https://charts.bitnami.com/bitnami',
    opts=pulumi.ResourceOptions(depends_on=[server_master]),
)

# Move kube config file from default K3S directory
server_master_move_kubeconfig = command.remote.Command('master_move_kubeconfig',
    connection=connection_master,
    create='mkdir -p ~/.kube && cp /etc/rancher/k3s/k3s.yaml ~/.kube/config',
    opts=pulumi.ResourceOptions(depends_on=[server_master_add_bitnami]),
)

# Deploy Nginx Helm chart
server_master_deploy_nginx = command.remote.Command('master_deploy_nginx',
    connection=connection_master,
    create='helm install litrepublicpoc-ec2-nginx bitnami/nginx-ingress-controller',
    opts=pulumi.ResourceOptions(depends_on=[server_master_move_kubeconfig]),
)

# Add the Bitnami repo to Helm
server_master_get_k3stoken = command.remote.Command('master_get_k3stoken',
    connection=connection_master,
    create='sudo cat /var/lib/rancher/k3s/server/node-token',
    opts=pulumi.ResourceOptions(depends_on=[server_master_deploy_nginx]),
)


#----------------------------------------------------------------------------------------------------------------------
# WORKER NODE DEFINITIONS
#----------------------------------------------------------------------------------------------------------------------


# TODO: Understand how to use kubectl contexts correctly

# Define the instance start-up scripting
server_worker1_userdata = """#!/bin/bash

# Update hostname
hostname="litrepublic-www-dev-worker1"
echo $hostname | tee /etc/hostname
sed -i '1s/.*/$hostname/' /etc/hosts
hostname $hostname

# Install K3S
curl -sfL https://get.k3s.io | K3S_URL=https://""" + str(server_master.private_ip) + """:6443 K3S_TOKEN=""" + str(server_master_get_k3stoken.stdout).strip() + """ sh -s - agent --write-kubeconfig-mode 644 --no-deploy traefik --no-deploy servicelb

"""
#curl -sfL https://get.k3s.io | K3S_URL=https://172.31.11.233:6443 K3S_TOKEN=K104e25bc173c7cfc4b24924413e9b56e222bae38e995bb1707b863cb601dfe47f0::server:c96e9d1be49e2751ee09dc50161a1558 sh -s --write-kubeconfig-mode 644 --no-deploy traefik --no-deploy servicelb
# Define our master node as an AWS EC2 instance
server_worker1 = aws.ec2.Instance('litrepublicpoc-www-dev-worker1',
    instance_type=size,
    vpc_security_group_ids=[admin_group.id], 
    user_data=server_worker1_userdata,
    ami=ami.id,
    key_name='LitRepublicPoc',
    tags={
        "Name":"litrepublicpoc-ec2-worker1"
    },
)

# Configure provisioner connection string to master node
connection_worker1 = command.remote.ConnectionArgs(
    host=server_worker1.public_ip,
    user='ubuntu',
    private_key=key,
)

# TODO: Implement Py FOR loop to check if K3S service and Helm have installed and are running before doing stuff
# Is there a Pulumi native way to achieve this?


#----------------------------------------------------------------------------------------------------------------------
# OUTPUT DEFINITIONS
#----------------------------------------------------------------------------------------------------------------------


# Current connection strings:
# ssh -i ~/.ssh/LitRepublicPoc.pem ubuntu@`aws ec2 describe-instances --filters Name=instance-state-name,Values=running Name=tag:Name,Values=litrepublicpoc-ec2-master --query 'Reservations[].Instances[].PublicDnsName' --output text`
# ssh -i ~/.ssh/LitRepublicPoc.pem ubuntu@`aws ec2 describe-instances --filters Name=instance-state-name,Values=running Name=tag:Name,Values=litrepublicpoc-ec2-worker1 --query 'Reservations[].Instances[].PublicDnsName' --output text`

# Export the public IP and hostname of the Amazon server to output
pulumi.export('Master Public IP', server_master.public_ip)
pulumi.export('Master Public hostname', server_master.public_dns)
pulumi.export('Worker1 public IP', server_worker1.public_ip)
pulumi.export('Worker1 public hostname', server_worker1.public_dns)
pulumi.export('K3S node token',server_master_get_k3stoken.stdout)
pulumi.export('Master private IP',server_master.private_ip)

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
    # activate the venv
        # source venv/bin/activate
    # install deps from requirements.txt into venv
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