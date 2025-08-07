# Kubernetes Environment Variable Update POC

This repository contains a proof-of-concept (POC) for automating the update of environment variables in Kubernetes deployments.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/heyamay/Kubernetes-Env-Update.git
    cd k8s-env-update-poc
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Minikube:**
    - Install Minikube and Docker on your WSL2 Ubuntu distribution.
    - Start a Minikube cluster:
      ```bash
      minikube start --driver=docker
      ```
    - Create the namespace and apply the sample deployment:
      ```bash
      kubectl create namespace fb-13-oracle
      kubectl apply -f deployment.yaml
      ```

## Usage

To update the environment variables of a deployment, run the `update_env.py` script:

```bash
python update_env.py --cluster QualityEdge --namespace fb-13-oracle --service data-archival-engine --ticket 12345 --engineer "John Doe" --env_vars env_vars.json
```

### Arguments

-   `--cluster`: The name of the cluster.
-   `--namespace`: The namespace of the service.
-   `--service`: The name of the service.
-   `--ticket`: The ticket ID for the change.
-   `--engineer`: The name of the engineer making the change.
-   `--env_vars`: The path to the JSON file with the environment variables.

## CI/CD

This project uses Jenkins for CI/CD. The `Jenkinsfile` in the root of the repository defines a pipeline that automates the process of updating the environment variables in a Kubernetes deployment.

### Jenkins Pipeline

The Jenkins pipeline is configured to do the following:

1.  **Checkout the code:** The pipeline checks out the code from the Git repository.
2.  **Run the update script:** The pipeline runs the `update_env.py` script with the parameters defined in the Jenkins UI.
3.  **Apply the changes:** The script updates the environment variables in the specified Kubernetes deployment.

To use the Jenkins pipeline, you will need to create a new pipeline job in Jenkins and configure it to use the `Jenkinsfile` from this repository.
