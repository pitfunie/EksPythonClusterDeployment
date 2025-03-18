# Importing the boto3 library for interacting with AWS services.
# boto3 is a powerful and widely used AWS SDK for Python that allows you to manage and automate AWS services,
# such as EC2, S3, EKS, IAM, CloudWatch, Lambda, and more. In this script, boto3 is essential for creating
# and managing EKS clusters, IAM roles, and related AWS resources.
import boto3

# Importing the json module, which is part of Python's standard library.
# This module is used to work with JSON (JavaScript Object Notation) data,
# such as reading configuration files in JSON format or processing JSON responses from AWS APIs.
# JSON is the standard format for configuring AWS resources, making this module crucial for parsing and validating input data.
import json

# Importing the warnings library from Python's standard library.
# This module is used to issue warning messages to the user for things like deprecated features or other non-fatal issues.
# In this script, it's utilized to notify the user about potential issues that don't stop the program but may need attention.
import warnings

# Importing ClientError from the botocore.exceptions module.
# botocore is a low-level, foundational library used by boto3 to make HTTP requests to AWS services.
# The ClientError exception specifically is used to catch and handle errors returned by AWS services,
# such as invalid permissions, resource not found, or service failures. This helps in providing meaningful error handling.
from botocore.exceptions import ClientError

# Importing the Thread class from Python's threading module.
# Threading allows concurrent execution of code in separate threads, which can improve performance for tasks
# that might otherwise block the main program (e.g., waiting for cluster creation to complete).
# In this script, threading is used to deploy EKS clusters or perform other tasks without blocking the main program flow.
from threading import Thread


# Enable warnings to notify users about potential issues in the script
warnings.simplefilter("always", UserWarning)


# Define a class to encapsulate the entire EKS Cluster setup process
class EKSClusterSetup:
    """
    A class to handle the creation and configuration of an Amazon EKS cluster.
    Includes methods for validating input configurations, creating necessary IAM roles,
    deploying the EKS cluster, and monitoring its status.
    """

    def __init__(self, cluster_name, region, config_file):
        """
        Initialize the class and set up AWS client connections.

        :param cluster_name: The name of the EKS cluster to be created.
        :param region: The AWS region where the cluster will be deployed.
        :param config_file: Path to a JSON file containing cluster configuration data.
        """
        self.cluster_name = cluster_name  # Name of the EKS cluster
        self.region = region  # AWS region for the cluster
        self.config_file = config_file  # Path to the configuration file
        self.eks_client = boto3.client("eks", region_name=self.region)  # AWS EKS client
        self.iam_client = boto3.client("iam", region_name=self.region)  # AWS IAM client
        self.sts_client = boto3.client("sts", region_name=self.region)  # AWS STS client
        self.validated = (
            False  # Flag to indicate whether the configuration is validated
        )

    def validate_config(self):
        """
        Validates the cluster configuration file to ensure all required fields are present.
        This method reads the configuration JSON file and checks for necessary keys like
        VPC settings, node role ARNs, and subnets.

        Raises exceptions if:
        - The file doesn't exist.
        - JSON is malformed.
        - Required keys are missing.
        """
        try:
            # Open and load the configuration file
            with open(self.config_file, "r") as file:
                config = json.load(file)
                print("Configuration loaded successfully.")  # Indicate successful load

            # List of required keys that must be in the configuration file
            required_keys = ["vpcConfig", "nodeRoleArn", "subnets"]
            for key in required_keys:
                # Check if any required key is missing
                if key not in config:
                    raise ValueError(f"Missing {key} in the configuration file.")

            self.validated = True  # Mark the configuration as valid
        except FileNotFoundError:
            # Handle case where the file is not found
            print("Error: Configuration file not found.")
            raise
        except json.JSONDecodeError:
            # Handle case where JSON is malformed
            print("Error: Invalid JSON in configuration file.")
            raise
        except Exception as e:
            # Handle other generic exceptions during validation
            print(f"Validation error: {e}")
            raise

    def create_iam_role(self):
        """
        Creates the IAM role necessary for the EKS cluster to function.
        The role allows EKS to interact with other AWS services (e.g., EC2, CloudFormation).

        :return: The ARN (Amazon Resource Name) of the created IAM role.
        Raises exceptions for AWS-related client errors.
        """
        try:
            print("Creating IAM role...")  # Notify user about role creation
            # Define the trust relationship policy for the EKS service
            response = self.iam_client.create_role(
                RoleName=f"{self.cluster_name}-role",  # Unique role name
                AssumeRolePolicyDocument=json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"Service": "eks.amazonaws.com"},
                                "Action": "sts:AssumeRole",
                            }
                        ],
                    }
                ),
            )
            print("IAM Role created successfully.")  # Confirm success
            return response["Role"]["Arn"]  # Return the role ARN
        except ClientError as error:
            # Handle AWS-specific client errors
            print(f"IAM Role creation failed: {error}")
            raise

    def create_eks_cluster(self):
        """
        Initiates the creation of an Amazon EKS cluster using the provided configuration.

        Requires:
        - Validated configuration file.
        - IAM role created using the create_iam_role method.

        Raises exceptions for invalid configurations or AWS client errors.
        """
        try:
            # Ensure the configuration has been validated before proceeding
            if not self.validated:
                raise RuntimeError("Configuration not validated.")

            print("Creating EKS cluster...")  # Notify user about cluster creation
            # Use the EKS client to create the cluster
            self.eks_client.create_cluster(
                name=self.cluster_name,  # Cluster name
                version="1.27",  # Kubernetes version
                roleArn=self.create_iam_role(),  # IAM role ARN
                resourcesVpcConfig=json.load(open(self.config_file))[
                    "vpcConfig"
                ],  # VPC settings
            )
            print("EKS Cluster creation initiated.")  # Indicate process start
        except ClientError as error:
            # Handle AWS-specific client errors
            print(f"EKS Cluster creation failed: {error}")
            raise

    def monitor_cluster_status(self):
        """
        Continuously monitors the status of the EKS cluster creation process.
        Prints updates on the cluster's status until it becomes active.
        """
        try:
            print("Monitoring cluster status...")  # Notify user about monitoring start
            while True:
                # Describe the cluster to fetch its current status
                response = self.eks_client.describe_cluster(name=self.cluster_name)
                status = response["cluster"]["status"]  # Extract status information
                print(f"Cluster status: {status}")  # Print the current status

                # Exit the loop when the cluster status is 'ACTIVE'
                if status == "ACTIVE":
                    print("Cluster is ready.")  # Confirm readiness
                    break
        except Exception as e:
            # Handle monitoring errors
            print(f"Error monitoring cluster: {e}")
            raise

    def deploy(self):
        """
        Executes the entire deployment process, including:
        - Configuration validation.
        - IAM role creation.
        - EKS cluster setup.
        - Monitoring cluster status.

        Handles all common errors gracefully with appropriate error messages.
        """
        try:
            print("Starting deployment...")  # Notify user about the start
            self.validate_config()  # Validate the configuration
            self.create_eks_cluster()  # Create the EKS cluster
            self.monitor_cluster_status()  # Monitor the cluster's status
            print("Deployment completed successfully.")  # Notify on success
        except PermissionError:
            # Handle permission-related issues
            print("Permission error detected.")
        except Exception as e:
            # Handle generic exceptions
            print(f"Deployment failed: {e}")


# Example Usage Section
if __name__ == "__main__":
    # Define key parameters for the cluster deployment
    cluster_name = "MyEKSCluster"  # Name of the cluster
    region = "us-east-1"  # AWS region for deployment
    config_file = "eks_config.json"  # Path to the JSON configuration file

    # Initialize the EKSClusterSetup class with specified parameters
    setup = EKSClusterSetup(cluster_name, region, config_file)
    # Use threading to deploy the cluster in a separate thread for efficiency
    setup_thread = Thread(target=setup.deploy)
    setup_thread.start()  # Start the deployment thread
    setup_thread.join()  # Wait for the deployment to finish
