# Check if EC2 key pair exists
keyexists=$(aws ec2 describe-key-pairs | jq '.KeyPairs[].KeyName' | grep LitRepublicPoc)

# Create keypair if it doesn't exist
if [ $? == "1" ]; then aws ec2 create-key-pair --key-name LitRepublicPoc --query 'KeyMaterial' --output text > ~/.ssh/LitRepublicPoc.pem; fi

# Display key pair SHA1 hash fingerprint
aws ec2 describe-key-pairs --key-name LitRepublicPoc --query 'KeyPairs[*].[KeyName,KeyFingerprint]' --output text

# Check if the security group exists
groupexists=$(aws ec2 describe-security-groups | jq '.SecurityGroups[].GroupName' | grep litrepublicpoc_sg_apsoutheast2)

# Create security group if it doesn't exist
if [ $? == "1" ]; then 
    aws ec2 create-security-group --group-name litrepublicpoc_sg_apsoutheast2 --description "Security Group for Amazon EC2 instance 1"
    aws ec2 authorize-security-group-ingress --group-name litrepublicpoc_sg_apsoutheast2 --protocol tcp --port 443 --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --group-name litrepublicpoc_sg_apsoutheast2 --protocol tcp --port 22 --cidr `curl https://checkip.amazonaws.com | awk '{ sub(/[.]([0-9]{2,3})$/,"&/32"); print }'`
fi

# Get the ID of the security group that will govern this instance
groupid=$(aws ec2 describe-security-groups --group-name litrepublicpoc_sg_apsoutheast2 --query 'SecurityGroups[].GroupId' --output text)

# Determine if an instance is already running
instanceexists=$(aws ec2 describe-instances | jq -c '.Reservations[].Instances[] | select(.Tags[]["Value"] == "awsec2-litrepublicpoc"), .State.Name' | grep 'running')

# Start the EC2 instance if it is not running and attach a name tag to the instance
if [ $? == "1" ]; then 
    aws ec2 run-instances --image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/amzn-ami-hvm-x86_64-gp2 --count 1 --instance-type t2.micro --key-name LitRepublicPoc --security-group-ids $groupid --tag-specifications 'ResourceType=instance,Tags=[{Key="Name",Value="awsec2-litrepublicpoc"}]'
fi

# Terminate the EC2 instance
# aws ec2 terminate-instances --instance-ids `aws ec2 describe-instances --filters Name=tag:Name,Values=awsec2-litrepublicpoc Name=instance-state-name,Values=running --query 'Reservations[].Instances[].InstanceId' --output text`

# Echo State of this EC2 Instance:
aws ec2 describe-instances | jq '.Reservations[].Instances[].Tags[].Value'
aws ec2 describe-instances | jq '.Reservations[].Instances[].State.Name'