

import argparse
import json
import os
from kubernetes import client, config
import base64

def update_deployment(cluster, namespace, service, ticket, engineer, env_vars_path):
    """
    Updates a Kubernetes deployment with environment variables from a JSON file.

    Args:
        cluster (str): The name of the cluster.
        namespace (str): The namespace of the deployment.
        service (str): The name of the deployment.
        ticket (str): The Azure DevOps ticket ID.
        engineer (str): The name of the DevOps engineer.
        env_vars_path (str): The path to the JSON file with environment variables.
    """

    try:
        # Load Kubernetes configuration
        try:
            config.load_kube_config()
        except config.ConfigException:
            # If running inside a pod, use in-cluster config
            config.load_incluster_config()

        api = client.AppsV1Api()
        core_api = client.CoreV1Api()

        # Read environment variables from the JSON file
        with open(env_vars_path, 'r') as f:
            env_vars = json.load(f)

        # Get the deployment
        deployment = api.read_namespaced_deployment(name=service, namespace=namespace)

        # --- Secret Handling ---
        secret_name = f"{service}-secrets"
        secret_data = {}

        # Identify sensitive data and add it to the secret_data dictionary
        if "INPUT_CONNECTION_CONFIG" in env_vars:
            try:
                connection_config = json.loads(env_vars["INPUT_CONNECTION_CONFIG"])
                if "password" in connection_config:
                    password = connection_config.pop("password")
                    secret_data["INPUT_CONNECTION_CONFIG_PASSWORD"] = base64.b64encode(password.encode("utf-8")).decode("utf-8")
                    env_vars["INPUT_CONNECTION_CONFIG"] = json.dumps(connection_config)
            except json.JSONDecodeError:
                print("Warning: INPUT_CONNECTION_CONFIG is not a valid JSON string. Cannot extract password.")


        if secret_data:
            # Create or update the secret
            try:
                secret = core_api.read_namespaced_secret(name=secret_name, namespace=namespace)
                secret.data.update(secret_data)
                core_api.replace_namespaced_secret(name=secret_name, namespace=namespace, body=secret)
                print(f"Updated secret '{secret_name}'")
            except client.ApiException as e:
                if e.status == 404:
                    secret = client.V1Secret(
                        api_version="v1",
                        kind="Secret",
                        metadata=client.V1ObjectMeta(name=secret_name, namespace=namespace),
                        type="Opaque",
                        data=secret_data
                    )
                    core_api.create_namespaced_secret(namespace=namespace, body=secret)
                    print(f"Created secret '{secret_name}'")
                else:
                    raise

        # --- Update Deployment Environment Variables ---
        container = deployment.spec.template.spec.containers[0]
        if container.env is None:
            container.env = []

        # Add/update environment variables
        for name, value in env_vars.items():
            env_var = client.V1EnvVar(name=name, value=value)
            # Check if the environment variable already exists
            found = False
            for i, existing_env_var in enumerate(container.env):
                if existing_env_var.name == name:
                    container.env[i] = env_var
                    found = True
                    break
            if not found:
                container.env.append(env_var)

        # Add environment variables from secrets
        for key in secret_data:
             env_var_from_secret = client.V1EnvVar(
                name=key,
                value_from=client.V1EnvVarSource(
                    secret_key_ref=client.V1SecretKeySelector(
                        name=secret_name,
                        key=key
                    )
                )
            )
             container.env.append(env_var_from_secret)


        # Apply the updated deployment
        api.patch_namespaced_deployment(name=service, namespace=namespace, body=deployment)
        print(f"Deployment '{service}' in namespace '{namespace}' updated successfully.")

        # --- Logging ---
        log_message = f"2025-08-06 17:41:23: {engineer} updated {service} in {namespace} for ticket {ticket}"
        with open("update_log.txt", "a") as log_file:
            log_file.write(log_message + "\n")
        print("Update logged.")


    except client.ApiException as e:
        print(f"Error updating deployment: {e.reason}")
    except FileNotFoundError:
        print(f"Error: Environment variables file not found at '{env_vars_path}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update environment variables in a Kubernetes deployment.")
    parser.add_argument("--cluster", required=True, help="The name of the cluster.")
    parser.add_argument("--namespace", required=True, help="The namespace of the service.")
    parser.add_argument("--service", required=True, help="The name of the service.")
    parser.add_argument("--ticket", required=True, help="The ticket ID for the change.")
    parser.add_argument("--engineer", required=True, help="The name of the engineer making the change.")
    parser.add_argument("--env_vars", required=True, help="The path to the JSON file with the environment variables.")

    args = parser.parse_args()

    update_deployment(args.cluster, args.namespace, args.service, args.ticket, args.engineer, args.env_vars)
