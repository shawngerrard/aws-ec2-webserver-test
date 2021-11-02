# aws-ec2-webserver-test

The purpose of this repository is to stand-up an AWS EC2 instance and use Lightweight Kubernetes (k3s) containers to run a persistent Wordpress instance that can be accessed publicly over HTTPS (443).

Rationale: To run a cloud-native POC for providing a web channel for a store.

**Note:** This guide differs from the instructions in [README.md](../README.md) in that we use language-agnostic [Pulumi](https://www.pulumi.com/) to build and manage our infrastructure code, rather than YAML code managed by Terraform, Helm, Ansible, etc.

We'll be using Python as our chosen language and AWS for resourcing our infrastructure, so make sure you [download and install Python v3 or above](https://www.python.org/downloads/). 

This guide assumes that you already have an AWS account, have set up AWS CLI, and can authenticate to AWS through CLI (either root or IAM).

Once you have Python3 installed, make sure you install ```venv``` with the command ```sudo pip3 install virtualenv ```. This is a tool to create isolated Python environments that contain all the necessary libraries to use the packages that a Python project will need. This is also useful to explicitly isolate different Python projects from each other to avoid any cross-contamination of code.

You'll also need to [install Pulumi](https://www.pulumi.com/docs/get-started/install/).

Process is split into three steps:
1. [Create and Configure a new Pulumi Project](#step1)
2. [Create an EC2 instance with K3S installed](#step2)
3. [Creating the EC2 instance](#step3)
4. [Installing Docker within the EC2 instance](#step4)
5. [Deploying the services via Docker containers](#step5)


## Step 1 - Create and Configure a new Pulumi Project <a href="step1"></a>

First, we need to create a directory to hold our project files. Then, we will run the Pulumi command to create a [Pulumi project](https://www.pulumi.com/docs/intro/concepts/project/) with some basic scaffolding based upon the cloud resources and programming language(s) we'll be using.

```
mkdir pulumi && cd pulumi
pulumi new aws-python
```

I've named the project directory *pulumi* and created a new aws-python Pulumi project.

The CLI will then prompt you to authenticate with the Pulumi server, and then you'll be asked to configure the general settings for your new [Pulumi stack](https://www.pulumi.com/docs/intro/concepts/stack/), such as project name and description. You may also be prompted to enter some AWS configuration settings, such as the default region for the project.

You can find information on the Pulumi website regarding some of [the files that are generated during project creation](https://www.pulumi.com/docs/get-started/aws/review-project/).


## Step 2 - Create an EC2 instance with K3S installed <a href="step2"></a>

### Define the AWS Infrastructure

When we created the project in [Step 1](#step1), Pulumi scaffolds a number of files and directories into the project directory. The file **__main__.py** is the default file that executes when we attempt to deploy cloud infrastructure.

I've added my [__main__.py](pulumi/__main__.py) file into the repository for you to use or modify.

My main script defines an Ubuntu [Amazon Machine Image (AMI)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html), a [Security Group](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html#VPCSecurityGroups), and then attaches these resources to a newly-defined EC2 instance.

A nifty feature of AWS is that we can also add some code to the [User-Data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html) attribute of the EC2 instance to define some scripts to run as the instance is starting up. This is useful if you want to install applications or modules into the instance automatically upon startup. In this case, we use the *user-data* attribute of our EC2 instance definition to install [Lightweight Kubernetes (K3S)](https://k3s.io/). 


### Deploy the AWS Infrastructure

So, we've built our infrastructure as Python code. Now, we need to deploy it and test that K3S has installed correctly.

Before we deploy our infrastructure, we'll need to secure and isolate our Pulumi project from other projects with a virtual environment (venv). 

Before we do this, check your project directory for a ```requirements.txt``` file. Open it (or create it, if for some reason the ```pulumi new``` command didn't scaffold the file for you, or you do not have the file from this .git repo), and ensure it contains the following lines:

```
pulumi>=3.0.0,<4.0.0
pulumi-aws>=4.0.0,<5.0.0
requests
```

This file informs Pulumi of the dependent packages needed for our Pulumi project. In this case, we want a version between 3 & 4 of Pulumi CLI, a version between 4 & 5 of the Pulumi AWS modules (in order to interact with AWS resources), and the Python *requests* module, which allows us to make API calls with Python3.

The following code will create a Python virtualenv, activate it, and install any dependencies from our *requirements.txt* file.

```
cd path/to/pulumi/project/folder
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

With our project dependencies installed, and our virtualenv activated, we're ready to deploy with the command ```pulumi up```.


## Step 2 - Installing Docker into Amazon EC2 <a href="step2"></a>

## Step 3 - Deploying Services via Docker <a href="step3"></a>