# Importing necessary libraries for infrastructure diagram creation and visualizations.
from diagrams import Diagram, Cluster
from diagrams.aws.management import Organizations
from diagrams.aws.network import VPC, PublicSubnet, PrivateSubnet, NATGateway, ClientVpn
from diagrams.aws.compute import EKS
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3
from diagrams.aws.network import CloudFront
from diagrams.cicd import GithubActions
from diagrams.programming.language import Python

import pandas as pd
import plotly.graph_objects as go  # For creating 3D interactive visualizations

# Data for AWS infrastructure visualization
data = {
    "Account": [
        "Management",
        "Development",
        "Staging",
        "Production",
    ],  # AWS Account names
    "EKS Clusters": [1, 3, 2, 4],  # Number of Kubernetes clusters in each account
    "RDS Instances": [1, 1, 2, 3],  # Number of database instances in each account
    "NAT Gateways": [1, 1, 2, 3],  # NAT Gateways for outbound Internet access
}

# Create a Pandas DataFrame to organize data
df = pd.DataFrame(data)


# Function for 3D motion visualization
def visualize_3d_motion(dataframe):
    """
    Create an interactive 3D scatter plot with multiple colors for AWS infrastructure resources.
    :param dataframe: A Pandas DataFrame containing AWS account data and resource counts.
    """
    fig = go.Figure()

    # Add scatter points for EKS Clusters using a blue color scheme
    fig.add_trace(
        go.Scatter3d(
            x=dataframe["Account"],  # X-axis: AWS Accounts
            y=dataframe["EKS Clusters"],  # Y-axis: EKS Clusters count
            z=dataframe["NAT Gateways"],  # Z-axis: NAT Gateways count
            mode="markers",
            marker=dict(
                size=10,
                color=dataframe["EKS Clusters"],  # Blue color gradient
                colorscale="Blues",  # Apply blue colors
                opacity=0.8,
            ),
            name="EKS Clusters (Blue)",
        )
    )

    # Add scatter points for RDS Instances using a green color scheme
    fig.add_trace(
        go.Scatter3d(
            x=dataframe["Account"],
            y=dataframe["RDS Instances"],
            z=dataframe["NAT Gateways"],
            mode="markers+lines",
            marker=dict(
                size=8,
                color=dataframe["RDS Instances"],  # Green color gradient
                colorscale="Greens",  # Apply green colors
                opacity=0.8,
            ),
            line=dict(color="green", width=2),  # Green connecting lines
            name="RDS Instances (Green)",
        )
    )

    # Add scatter points for NAT Gateways using a red color scheme
    fig.add_trace(
        go.Scatter3d(
            x=dataframe["Account"],
            y=dataframe["NAT Gateways"],
            z=dataframe["EKS Clusters"],
            mode="markers",
            marker=dict(
                size=6,
                color=dataframe["NAT Gateways"],  # Red color gradient
                colorscale="Reds",  # Apply red colors
                opacity=0.7,
            ),
            name="NAT Gateways (Red)",
        )
    )

    # Layout customization for better visuals
    fig.update_layout(
        title="3D Motion Visualization of AWS Resources (Multi-Color)",
        scene=dict(
            xaxis_title="AWS Account",  # Label for X-axis
            yaxis_title="Resource Count (Clusters / Instances / Gateways)",  # Label for Y-axis
            zaxis_title="Cross-Resource Count",  # Label for Z-axis
        ),
        margin=dict(l=0, r=0, b=0, t=40),  # Adjust margins for better space
        legend=dict(
            x=0.1,
            y=0.9,
            bgcolor="rgba(255, 255, 255, 0.6)",  # Legend background
            bordercolor="black",
            borderwidth=1,  # Legend border
        ),
    )

    # Show the interactive 3D plot
    fig.show()


# Infrastructure Diagram using the Diagrams library
with Diagram("Innovate Inc. Infrastructure", show=True, direction="TB"):
    # AWS Accounts
    management_account = Organizations("Management Account")
    dev_account = Organizations("Development Account")
    staging_account = Organizations("Staging Account")
    prod_account = Organizations("Production Account")

    # Management Account Resources
    with Cluster("Management Account"):
        management_vpc = VPC("Management VPC")
        ClientVpn("VPN Gateway") - management_vpc

    #
    # Development Account Resources
    with Cluster("Development Account"):
        dev_vpc = VPC("Development VPC")
        dev_public = PublicSubnet("Public Subnet")
        dev_private = PrivateSubnet("Private Subnet")
        nat_gateway_dev = NATGateway("NAT Gateway")
        eks_dev = EKS("Development EKS Cluster")
        rds_dev = RDS("Development RDS")
        dev_vpc >> [dev_public, dev_private]
        dev_private >> eks_dev >> rds_dev
        dev_public >> nat_gateway_dev

    # Staging Account Resources
    with Cluster("Staging Account"):
        staging_vpc = VPC("Staging VPC")
        staging_public = PublicSubnet("Public Subnet")
        staging_private = PrivateSubnet("Private Subnet")
        nat_gateway_staging = NATGateway("NAT Gateway")
        eks_staging = EKS("Staging EKS Cluster")
        rds_staging = RDS("Staging RDS")
        staging_vpc >> [staging_public, staging_private]
        staging_private >> eks_staging >> rds_staging
        staging_public >> nat_gateway_staging

    # Production Account Resources
    with Cluster("Production Account"):
        prod_vpc = VPC("Production VPC")
        prod_public = PublicSubnet("Public Subnet")
        prod_private = PrivateSubnet("Private Subnet")
        nat_gateway_prod = NATGateway("NAT Gateway")
        eks_prod = EKS("Production EKS Cluster")
        rds_prod = RDS("Production RDS (Multi-AZ)")
        prod_vpc >> [prod_public, prod_private]
        prod_private >> eks_prod >> rds_prod
        prod_public >> nat_gateway_prod

    # Static Frontend Hosting
    with Cluster("Frontend Hosting"):
        cloudfront = CloudFront("CloudFront CDN")
        s3_static = S3("React Static Assets")
        cloudfront >> s3_static

    # CI/CD Pipeline Integration
    with Cluster("CI/CD Integration"):
        github_ci = GithubActions("GitHub Actions")
        argo_cd = Python("Argo CD")
        github_ci >> argo_cd >> [EKS("Deploy to EKS Clusters")]

    # Connectivity between Accounts and Frontend Hosting
    management_account >> [dev_account, staging_account, prod_account]
    prod_account >> cloudfront

# Main Execution
if __name__ == "__main__":
    # Generate the 3D motion visualization
    visualize_3d_motion(df)
