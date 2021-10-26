# Import modules
import pulumi
import requests
import pulumi_aws as aws

# Set variable constants
size = 't2.micro'
extip = requests.get('http://checkip.amazonaws.com/')

# Define Amazon Machine Image to use
ami = aws.get_ami(most_recent="true",
                  owners=["137112412989"],
                  filters=[{"name":"name","values":["amzn-ami-hvm-*"]}])

# Define administrator security group to allow SSH & HTTP access
group = aws.ec2.SecurityGroup('administrator-sg-litrepublicpoc',
    description='Enable SSH and HTTP access for Lit Republic',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': [extip.text.strip()+'/32'] },
        { 'protocol': 'tcp', 'from_port': 8080, 'to_port': 8080, 'cidr_blocks': ['0.0.0.0/0'] }
    ])

# Define the AWS EC2 instance to start
server = aws.ec2.Instance('litrepublicpoc-www',
    instance_type=size,
    vpc_security_group_ids=[group.id], # reference security group from above
    ami=ami.id)

# Export the public IP and hostname of the Amazon server
pulumi.export('publicIp', server.public_ip)
pulumi.export('publicHostName', server.public_dns)