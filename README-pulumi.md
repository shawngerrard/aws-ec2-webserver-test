# aws-ec2-webserver-test

The purpose of this repository is to stand-up an AWS EC2 instance and use Lightweight Kubernetes (k3s) containers to run a persistant Wordpress instance that can be accessed publicly over HTTPS (443).

Rationale: To run a cloud-native POC for providing a web channel for a store.

**Note:** This guide differs from the instructions in *README.md* in that we use language-agnostic [Pulumi](https://www.pulumi.com/) to build and manage our infrastructure code, rather than YAML code managed by Terraform, Helm, Ansible, etc.

We'll be using Python as our chosen language and AWS for resourcing our infrastructure, so make sure you [download and install Python v3 or above](https://www.python.org/downloads/).

This guide assumes that you already have an AWS account, have set up AWS CLI, and can authenticate to AWS through CLI (either root or IAM).

You'll also need to [install Pulumi](https://www.pulumi.com/docs/get-started/install/).

Process is split into three steps:
1. [Create and Configure a new Pulumi Project](#step1)
2. [Create an EC2 instance with HTTPS and SSH access](#step2)
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


## Step 2 - Installing Docker into Amazon EC2 <a href="step2"></a>

## Step 3 - Deploying Services via Docker <a href="step3"></a>