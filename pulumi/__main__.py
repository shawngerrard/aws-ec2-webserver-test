import pulumi
import pulumi_aws as aws
import requests

# Define constants
size = 't2.micro'
extipApiEndPoint = 'https://checkip.amazonaws.com'

# Set resource AMI to use
ami = aws.get_ami(most_recent="true",
                  owners=["137112412989"],
                  filters=[{"name":"name","values":["amzn-ami-hvm-*"]}])

# Get external IP from Amazon API
apiresponse = requests.get(extipApiEndPoint)

# Create a security group for the resource
group = aws.ec2.SecurityGroup('awsec2-sg-litrepublicpoc',
    description='Enable SSH access',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0'] }
    ])

server = aws.ec2.Instance('webserver-litrepublicpoc-www',
    instance_type=size,
    vpc_security_group_ids=[group.id], # reference security group from above
    ami=ami.id)

pulumi.export('publicIp', server.public_ip)
pulumi.export('publicHostName', server.public_dns)