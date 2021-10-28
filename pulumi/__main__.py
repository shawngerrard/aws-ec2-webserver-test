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
user_data = """
#!/bin/bash
curl -o k3s.sh -sfL https://get.k3s.io
cat k3s.sh
chmod +x k3s.sh
./k3s.sh
echo "<html><head><title>Lit Republic WWW Test</title></head><body>Well, helo thar fren!</body></html>" > index.html
"""

# Removed:
#curl -LO -v https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
#sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Define the AWS EC2 instance to start
server = aws.ec2.Instance('litrepublicpoc-www',
    instance_type=size,
    vpc_security_group_ids=[group.id], # Reference security group from above
    user_data = user_data, # Reference user data above
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