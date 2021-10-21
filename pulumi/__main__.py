import pulumi
import requests
import pulumi_aws as aws

# set constants
size = 't2.micro'
extip = requests.get('http://checkip.amazonaws.com/')

ami = aws.get_ami(most_recent="true",
                  owners=["137112412989"],
                  filters=[{"name":"name","values":["amzn-ami-hvm-*"]}])

group = aws.ec2.SecurityGroup('administrator-sg-litrepublicpoc',
    description='Enable SSH access',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': [extip.text.strip()+'/32'] }
    ])

server = aws.ec2.Instance('litrepublicpoc-www',
    instance_type=size,
    vpc_security_group_ids=[group.id], # reference security group from above
    ami=ami.id)

pulumi.export('publicIp', server.public_ip)
pulumi.export('publicHostName', server.public_dns)