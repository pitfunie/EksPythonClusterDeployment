Here’s an example walkthrough:

1. **Prepare Configuration:** 
   Assume you’ve created a dev_config.json file with the following content:
   {
    "cluster_name": "dev-cluster",
    "role_arn": "arn:aws:iam::123456789012:role/EKS-Cluster-Role",
    "subnet_ids": ["subnet-abc123", "subnet-def456"],
    "security_group_ids": ["sg-123abc"],
    "autoscaling_group_name": "EKS-Dev-AutoScaling-Group",
    "desired_capacity": 2
}
2. **Set Environment Variables:**
   export API_KEY="example_api_key"
   export DB_PASSWORD="example_db_password"

3. **Run the Script: Execute the script:**
   python deploy_eks.py

4. **Respond to Prompt: Enter the environment:**
   Enter the environment (dev, staging, production): dev
5. **View Output Logs: You’ll see logs like:**
   Successfully loaded configuration file: dev_config.json
   EKS cluster 'dev-cluster' creation initiated successfully.
   CloudWatch alarm configured for cluster 'dev-cluster'.
   Auto Scaling Group 'EKS-Dev-AutoScaling-Group' scaled to 2 instances.

