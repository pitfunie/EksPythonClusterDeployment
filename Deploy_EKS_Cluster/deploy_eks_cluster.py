# Import libraries
import boto3  # AWS SDK for Python to interact with AWS services
import json  # For reading and parsing JSON configuration files
import os  # For accessing environment variables
import warnings  # To issue runtime warnings
import traceback  # For capturing and logging detailed stack traces in error scenarios
import logging  # For tracking execution flow and errors

# Configure logging settings to output execution information and errors
logging.basicConfig(
    level=logging.INFO,  # Set logging level to display informational and higher-priority messages
    format="%(asctime)s - %(levelname)s - %(message)s",  # Define the format for log messages
    handlers=[logging.StreamHandler()],  # Output logs to the console
)


def load_config(environment):
    """
    Load configuration settings for a specific environment (e.g., 'dev', 'staging', 'production').

    Parameters:
        environment (str): Specifies the deployment environment.

    Returns:
        dict: A dictionary containing merged configuration settings loaded from a JSON file and environment variables.

    Raises:
        ValueError: If the environment name is missing or required keys in the configuration are invalid.
    """
    if not environment:
        raise ValueError("Environment parameter is required and cannot be empty!")

    # Construct the configuration file name based on the specified environment
    config_file = f"{environment}_config.json"
    config = {}

    # Load configuration from a JSON file
    try:
        with open(config_file, "r") as file:
            config = json.load(file)
        logging.info(f"Successfully loaded configuration file: {config_file}")
    except FileNotFoundError:
        warnings.warn(
            f"Configuration file '{config_file}' not found. Verify the file path.",
            RuntimeWarning,
        )
    except PermissionError:
        warnings.warn(
            f"Insufficient permissions to read configuration file '{config_file}'.",
            RuntimeWarning,
        )
    except json.JSONDecodeError as e:
        warnings.warn(
            f"Error decoding JSON in configuration file '{config_file}': {e}",
            RuntimeWarning,
        )
    except Exception:
        warnings.warn(
            f"Unexpected error occurred while reading '{config_file}':\n{traceback.format_exc()}",
            RuntimeWarning,
        )

    # Load sensitive data (e.g., API keys, passwords) from environment variables
    config["api_key"] = os.getenv("API_KEY", None)  # Fetch API key
    config["db_password"] = os.getenv("DB_PASSWORD", None)  # Fetch database password

    # Define a list of required keys for the configuration
    required_keys = [
        "cluster_name",
        "role_arn",
        "subnet_ids",
        "security_group_ids",
        "autoscaling_group_name",
        "desired_capacity",
    ]

    # Check if all required keys are present and valid in the configuration
    for key in required_keys:
        if key not in config or not config[key]:
            warnings.warn(
                f"Missing or invalid required configuration key: {key}", RuntimeWarning
            )

    # Issue warnings for any missing sensitive data
    if not config.get("api_key"):
        warnings.warn(
            "API_KEY environment variable is not set. This may cause issues.",
            RuntimeWarning,
        )
    if not config.get("db_password"):
        warnings.warn(
            "DB_PASSWORD environment variable is not set. This may cause issues.",
            RuntimeWarning,
        )

    return config


def create_eks_cluster(
    cluster_name, role_arn, subnet_ids, security_group_ids, region="us-east-1"
):
    """
    Create an Amazon Elastic Kubernetes Service (EKS) cluster.

    Parameters:
        cluster_name (str): Name of the EKS cluster to be created.
        role_arn (str): AWS IAM Role ARN for the cluster.
        subnet_ids (list): List of subnet IDs where the cluster will operate.
        security_group_ids (list): List of security group IDs for cluster network settings.
        region (str): AWS region where the cluster will be deployed. Default is 'us-east-1'.

    Returns:
        dict: API response containing details about the EKS cluster creation.

    Raises:
        ValueError: If any required parameter is missing or invalid.
    """
    if not cluster_name or not role_arn or not subnet_ids or not security_group_ids:
        raise ValueError(
            "All parameters (cluster_name, role_arn, subnet_ids, security_group_ids) are required!"
        )

    try:
        eks_client = boto3.client("eks", region_name=region)
        response = eks_client.create_cluster(
            name=cluster_name,
            roleArn=role_arn,
            resourcesVpcConfig={
                "subnetIds": subnet_ids,
                "securityGroupIds": security_group_ids,
            },
        )
        logging.info(f"EKS cluster '{cluster_name}' creation initiated successfully.")
        return response
    except Exception:
        logging.error(
            f"Failed to create the EKS cluster '{cluster_name}':\n{traceback.format_exc()}"
        )
        return {}


def configure_cloudwatch(cluster_name, namespace, region="us-east-1"):
    """
    Configure AWS CloudWatch alarms to monitor the health of an EKS cluster.

    Parameters:
        cluster_name (str): Name of the cluster for which monitoring is configured.
        namespace (str): CloudWatch metrics namespace for the cluster.
        region (str): AWS region where CloudWatch is configured. Default is 'us-east-1'.

    Returns:
        None
    """
    if not cluster_name or not namespace:
        raise ValueError("Both 'cluster_name' and 'namespace' are required!")

    try:
        cloudwatch_client = boto3.client("cloudwatch", region_name=region)
        cloudwatch_client.put_metric_alarm(
            AlarmName=f"{cluster_name}_Health",
            MetricName="ClusterHealth",
            Namespace=namespace,
            Period=300,
            EvaluationPeriods=1,
            Threshold=1.0,
            ComparisonOperator="LessThanThreshold",
            AlarmActions=[
                "arn:aws:sns:region:account-id:topic-name"
            ],  # Replace with your actual SNS ARN
            Statistic="Average",
        )
        logging.info(f"CloudWatch alarm configured for cluster '{cluster_name}'.")
    except Exception:
        logging.error(
            f"Failed to configure CloudWatch for cluster '{cluster_name}':\n{traceback.format_exc()}"
        )


def scale_worker_nodes(autoscaling_group_name, desired_capacity, region="us-east-1"):
    """
    Scale worker nodes for an EKS cluster via Auto Scaling Groups.

    Parameters:
        autoscaling_group_name (str): Name of the Auto Scaling Group to scale.
        desired_capacity (int): Desired number of worker nodes.
        region (str): AWS region for the Auto Scaling Group. Default is 'us-east-1'.

    Returns:
        dict: API response from the Auto Scaling Group scaling action.

    Raises:
        ValueError: If autoscaling_group_name or desired_capacity parameters are invalid.
    """
    if not autoscaling_group_name or desired_capacity is None:
        raise ValueError(
            "Both 'autoscaling_group_name' and 'desired_capacity' are required!"
        )

    try:
        autoscaling_client = boto3.client("autoscaling", region_name=region)
        response = autoscaling_client.set_desired_capacity(
            AutoScalingGroupName=autoscaling_group_name,
            DesiredCapacity=desired_capacity,
            HonorCooldown=True,
        )
        logging.info(
            f"Auto Scaling Group '{autoscaling_group_name}' scaled to {desired_capacity} instances."
        )
        return response
    except Exception:
        logging.error(
            f"Failed to scale worker nodes in Auto Scaling Group '{autoscaling_group_name}':\n{traceback.format_exc()}"
        )
        return {}


# Main execution entry point
if __name__ == "__main__":
    try:
        # Prompt user for environment and load corresponding configuration
        environment = input(
            "Enter the environment (dev, staging, production): "
        ).strip()
        config = load_config(environment)
        if not config:
            raise Exception("Configuration could not be loaded. Exiting program.")

        # Create an EKS cluster
        create_response = create_eks_cluster(
            cluster_name=config.get("cluster_name"),
            role_arn=config.get("role_arn"),
            subnet_ids=config.get("subnet_ids"),
            security_group_ids=config.get("security_group_ids"),
        )
        print("EKS Cluster Creation Response:", create_response)

        # Configure CloudWatch monitoring
        configure_cloudwatch(
            cluster_name=config.get("cluster_name"), namespace="AWS/EKS"
        )

        # Scale worker nodes in the cluster
        scaling_response = scale_worker_nodes(
            autoscaling_group_name=config.get("autoscaling_group_name"),
            desired_capacity=config.get("desired_capacity"),
        )
        print("Scaling Response:", scaling_response)

    except Exception:
        logging.critical(
            f"Critical error occurred during execution:\n{traceback.format_exc()}"
        )
