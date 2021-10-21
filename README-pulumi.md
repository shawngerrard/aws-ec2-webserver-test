# aws-ec2-webserver-test

The purpose of this repository is to automatically stand-up an AWS EC2 instance using Docker containers to run a persistant Wordpress instance.

Rationale: To run a POC for providing a web presence for a store.

**Note:** This guide differs from the instructions in *README.md* in that we use language-agnostic [Pulumi](https://www.pulumi.com/) to build and manage our infrastructure code, rather than YAML code managed by Terraform, Helm, Ansible, etc.

We'll be using Python as our chosen language and AWS for resourcing our infrastructure.

This guide assumes that you already have an AWS account, have set up AWS CLI, and can authenticate to AWS through CLI (either root or IAM).

You'll also need to [install Pulumi](https://www.pulumi.com/docs/get-started/install/).

Process is split into three steps:
1. [Creating the EC2 instance](#step1)
2. [Installing Docker within the EC2 instance](#step2)
3. [Deploying the services via Docker containers](#step3)

## Step 1 - Creating the Amazon EC2 Instance <a href="step1"></a>

## Step 2 - Installing Docker into Amazon EC2 <a href="step2"></a>

## Step 3 - Deploying Services via Docker <a href="step3"></a>