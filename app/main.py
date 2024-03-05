import os
import requests
import boto3
import json
import time
from datetime import datetime, timedelta
import urllib.parse

timestamp = datetime.today() - timedelta(hours=8)
formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

def check_api_response(response):
    if response.status_code not in [200, 201, 202, 204]:
        raise Exception(f"API Error: {response.status_code}: {response.content}")
    return response.json()

def load_from_s3(obj_bucket, obj_id, obj_key, obj_url, s3key_file, file):
    try:
        s3_client = boto3.client('s3',endpoint_url=obj_url, aws_access_key_id=obj_id, aws_secret_access_key=obj_key)
        pbix_file = s3_client.get_object(Bucket=obj_bucket, Key=s3key_file)
        with open(file, 'wb') as local_file:
            local_file.write(pbix_file['Body'].read())
        return file
    except Exception as e:
        raise Exception(f"S3 Error: {str(e)}")

def api_get_token(client_id, client_secret, tenant_id):
    data = {
        "client_id": {client_id},
        "grant_type": "client_credentials",
        "resource": "https://analysis.windows.net/powerbi/api",
        "response_mode": "query",
        "client_secret": {client_secret},
    }
    response = requests.get(
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/token", data=data
    )
    check_api_response(response)
    access_token = response.json()["access_token"]
    token = {"Authorization": f"Bearer {access_token}"}
    return token

def api_deploy_report(workspace_id, token, file):
    if file.endswith(".pbix"):
        file_name = os.path.basename(file)
        display_name = file_name.replace('_', ' ')[:-5]
        file_import = {'file': open(file_name, 'rb')}
        response = requests.post(
            (f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?"
            f"datasetDisplayName={urllib.parse.quote(display_name)}"
            f"&nameConflict=CreateOrOverwrite"),
            headers=token,
            files=file_import
            )
        response_json = check_api_response(response)
        print(response_json)
        return display_name, file_name

def archive_to_s3(obj_bucket, obj_id, obj_key, obj_url, file_name, s3_key_archive):
    try:
        s3_client = boto3.client('s3',endpoint_url=obj_url, aws_access_key_id=obj_id, aws_secret_access_key=obj_key)
        with open(file_name, 'rb') as body_file:
            file_bytes = body_file.read()
        s3_client.put_object(Bucket = obj_bucket, Key=s3_key_archive, Body=file_bytes)

        # Test to compare boto3 session with boto3 client
        # session = boto3.Session(aws_access_key_id=obj_id, aws_secret_access_key=obj_key)
        # s3_resource = session.resource('s3', endpoint_url=obj_url)
        # bucket = s3_resource.Bucket(obj_bucket)
        # bucket.put_object(Key=s3_key_archive, Body=file_bytes)

    except Exception as e:
        raise Exception(f"S3 Error: {str(e)}")

def api_get_report_id(token, display_name, workspace_id):
    response = requests.get(
        f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports",
        headers=token
        )
    response_json = check_api_response(response)["value"]
    for report in response_json:
        if (
            report["reportType"] == "PowerBIReport"
            and report["name"] == display_name
        ):
            print(f"Report ID Match: {report}")
            dataset_id = report['datasetId']
            return dataset_id

def api_add_users(token, obj_bucket, obj_id, obj_key, obj_url, s3key_users, dataset_id, workspace_id):
    s3_client = boto3.client('s3',endpoint_url=obj_url, aws_access_key_id=obj_id, aws_secret_access_key=obj_key)
    txt_file = s3_client.get_object(Bucket = obj_bucket, Key=s3key_users)
    with open('users.txt', 'wb') as local_file:
        local_file.write(txt_file['Body'].read())
    with open('users.txt', 'r') as file:
        for line in file:
            user = line.strip()
            print(user)
            data = {
                "identifier": user,
                "principalType": "User",
                "datasetUserAccessRight": "Read"
                }
            response = requests.post(
                f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/users",
                headers=token, data=data
                )
            # f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/users"
            print(f"Access added: {data}:{response}")

def main():
    try:
        # User Input
        file = os.environ.get("PBI_FILE")
        env = os.environ.get("WORKSPACE_ENV")
        domain = os.environ.get("DOMAIN")

        # Power BI API Service Principal
        client_id = os.environ.get("CLIENT_ID")
        client_secret =  os.environ.get("CLIENT_SECRET")

        # Object Storage Credentials
        obj_bucket = os.environ.get("OBJ_BUCKET")
        obj_id = os.environ.get("OBJ_ID")
        obj_key = os.environ.get("OBJ_KEY")
        obj_url= 'https://nrs.objectstore.gov.bc.ca'

        # IDs for BCGov Azure Tenant and NRM Workspaces
        tenant_id = '6fdb5200-3d0d-4a8a-b036-d3685e359adc'
        if env == 'dev':
            workspace_id ='c7ef19d0-b230-4b9e-89e2-984fccc75198'
        elif env == 'test':
            workspace_id =  '5b2835d9-510c-495c-b915-b24c52aacd05'
        elif env == 'prod':
            workspace_id =  '3c32cb15-e9fd-4a2b-9ded-a58ab3f5b637'
        else:
            raise ValueError("Invalid environment specified")

        # Load PBI file from S3
        s3key_file = f'nr_powerbi_workspace_deploy/{env}/{domain}/{file}'
        file = load_from_s3(obj_bucket, obj_id, obj_key, obj_url, s3key_file, file)
        print(f'Successfully loaded {file} from S3 bucket')

        # Get API token
        token = api_get_token(client_id, client_secret, tenant_id)
        print("API token aquired")

        # Deploy PBI file to NRM workspace
        display_name, file_name = api_deploy_report(workspace_id, token, file)
        print(f'Successfully deployed {file} to {env} Power BI workspace')

        # Create record of deployment in 'archive' folder
        s3_key_archive = f'nr_powerbi_workspace_deploy/{env}/{domain}/archive/{display_name} - {formatted_timestamp}.pbix'

        archive_to_s3(obj_bucket, obj_id, obj_key, obj_url, file_name, s3_key_archive)
        print(f'Successfully archived {file} in object storage')

        # Grant users access
        # s3key_users = f'nr_powerbi_workspace_deploy/{env}/{domain}/users.txt'
        # dataset_id = api_get_report_id(token, display_name, workspace_id)
        # api_add_users(token, obj_bucket, obj_id, obj_key, obj_url, s3key_users, dataset_id, workspace_id)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()