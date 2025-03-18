# EKS Cluster Deployment Script

This Python script automates the process of creating and configuring an Amazon Elastic Kubernetes Service (EKS) cluster. It includes functionality for validating input configurations, creating necessary IAM roles, initiating EKS cluster deployment, and monitoring cluster status.

## Features
- **Configuration Validation**: Ensures that required keys are present in the provided JSON configuration file.
- **IAM Role Creation**: Automatically creates the necessary IAM role with appropriate permissions.
- **Cluster Deployment**: Deploys the EKS cluster based on the provided configurations.
- **Status Monitoring**: Monitors the cluster creation process until it is active.

## Prerequisites
- Install Python (>= 3.7).
- Install the AWS SDK for Python (Boto3): `pip install boto3`.
- Provide an Amazon Web Services (AWS) account with proper permissions.
- Prepare a JSON configuration file (e.g., `eks_config.json`) with the following structure:
  ```json
  {
    "vpcConfig": {
      "subnetIds": ["subnet-abc123", "subnet-def456"],
      "securityGroupIds": ["sg-xyz789"]
    },
    "nodeRoleArn": "arn:aws:iam::123456789012:role/EKSNodeRole",
    "subnets": ["subnet-abc123", "subnet-def456"]
  }

1. **Clone or download this repository.**

2. **Install the required Python libraries:**
   pip install boto3 botocore

    Usage
    To use the script, initialize the EKSClusterSetup class and call the deploy() method.   

***Example Deployment***

1. ## Modify the config_file path to point to your JSON configuration file (e.g., eks_config.json).

2. **Run the script:**

    python eks_cluster_setup.py
    
    Below is a quick example to get started:
    from threading import Thread

# Import the EKSClusterSetup class from the script
    from eks_cluster_setup import EKSClusterSetup

# Define parameters
    cluster_name = "MyEKSCluster"
    region = "us-east-1"
    config_file = "eks_config.json"

# Initialize the EKSClusterSetup class
    setup = EKSClusterSetup(cluster_name, region, config_file)

# Use threading for efficiency
    setup_thread = Thread(target=setup.deploy)
    setup_thread.start()
    setup_thread.join()

## Error Handling

## The script provides meaningful error messages for:

    Missing or invalid configuration files.

    AWS permission errors.

    EKS or IAM service-related issues.

## Notes

    Ensure AWS credentials are correctly configured (e.g., using the AWS CLI or environment variables).

    Use proper IAM permissions to run the script.