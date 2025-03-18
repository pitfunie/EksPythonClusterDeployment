**Step-by-Step Example Execution**

1. **Install Necessary Libraries**
Run the following commands in your terminal to install required Python libraries:
pip install diagrams pandas plotly

If graphviz is not installed on your system (required for the diagrams library):
sudo apt-get install graphviz
brew install graphviz
pip install graph

 Input Data
AWS Resource Data

The code uses a Python dictionary (data) to represent AWS accounts and their associated resources:

data = {
    "Account": ["Management", "Development", "Staging", "Production"],
    "EKS Clusters": [1, 3, 2, 4],
    "RDS Instances": [1, 1, 2, 3],
    "NAT Gateways": [1, 1, 2, 3],
}


2. **Save the Code**
   Save the provided Python code in a file called aws_infrastructure.py.

3. **Run the Script**
   python aws_infrastructure.py

4. **What Happens During Execution**
   3D Interactive Visualization:

   The visualize_3d_motion(df) function will create an interactive 3D scatter plot.

   Data Used: The data dictionary (AWS account and resource data) is converted into a 
   Pandas DataFrame (df) and visualized in 3D.

    Output: A browser window opens showing an interactive plot:
        X-axis: AWS Account names (e.g., Management, Development).
        Y-axis: Resource count for EKS Clusters, RDS Instances, or NAT Gateways.
        Z-axis: Cross-resource relationships (e.g., linking NAT Gateways with EKS/RDS).
        Color-coded Points: Blue for EKS Clusters, Green for RDS Instances, 
        Red for NAT Gateways. 

5. **AWS Architecture Diagram:** 
     The diagrams library generates a graphical diagram of AWS infrastructure.

     Clusters Used: The script creates separate clusters for each AWS account (e.g., 
     Management, Development, etc.).

     Output: A PNG file named Innovate Inc. Infrastructure.png is created in the script’s 
     directory.

     Example Layout:

        VPCs, public/private subnets, NAT Gateways, EKS clusters, and RDS instances are 
        visually connected.

    Separate clusters for Management, Development, Staging, and Production accounts.
    Additional clusters show frontend hosting with CloudFront and S3, along with a CI/CD 
    pipeline using GitHub Actions and Argo CD.  

***Sample Outputs***
3D Visualization Example

When you run the script, a browser window will display a 3D scatter plot:

    EKS Clusters (Blue): Indicates Kubernetes clusters in various AWS accounts.

    RDS Instances (Green): Shows databases across accounts.

    NAT Gateways (Red): Displays outbound gateways for each account.

    Points and lines provide a 3D overview of the infrastructure.

You can rotate, zoom, and interact with the visualization to analyze the relationships between resources.       