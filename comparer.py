import os
import difflib
import csv
import json
import pandas as pd
from PyPDF2 import PdfReader
import boto3
from azure.storage.blob import BlobServiceClient

def read_local_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def read_s3_file(bucket_name, file_key):
    s3_client = boto3.client('s3')
    s3_object = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    return s3_object['Body'].read().decode('utf-8').splitlines()

def read_azure_blob(connection_string, container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_data = blob_client.download_blob()
    return blob_data.content_as_text().splitlines()

def get_file_contents(file_location):
    # Determine the source of the file and fetch the contents
    if file_location.startswith("s3://"):
        bucket_name, file_key = file_location[5:].split('/', 1)
        return read_s3_file(bucket_name, file_key)
    elif file_location.startswith("azure://"):
        connection_string, container_name, blob_name = file_location[8:].split('/', 2)
        return read_azure_blob(connection_string, container_name, blob_name)
    else:
        return read_local_file(file_location)

def compare_text_files(file1_contents, file2_contents):
    diff = difflib.unified_diff(file1_contents, file2_contents, lineterm='')
    return '\n'.join(list(diff))

def compare_csv(file1, file2):
    file1_df = pd.read_csv(file1)
    file2_df = pd.read_csv(file2)
    return compare_dataframes(file1_df, file2_df)

def compare_excel(file1, file2):
    file1_df = pd.read_excel(file1, sheet_name=None)
    file2_df = pd.read_excel(file2, sheet_name=None)
    
    diffs = []
    for sheet in file1_df.keys():
        if sheet in file2_df:
            diff = compare_dataframes(file1_df[sheet], file2_df[sheet])
            if diff:
                diffs.append(f"Differences in sheet '{sheet}':\n{diff}")
    return "\n".join(diffs)

def compare_dataframes(df1, df2):
    diff = pd.concat([df1, df2]).drop_duplicates(keep=False)
    if not diff.empty:
        return diff.to_string()
    return ""

def compare_json(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        json1 = json.load(f1)
        json2 = json.load(f2)
        
    return json_diff(json1, json2)

def json_diff(json1, json2, path=""):
    diffs = []
    for key in json1.keys():
        if key not in json2:
            diffs.append(f"Missing key in json2: {path + key}")
        else:
            if isinstance(json1[key], dict):
                diffs.extend(json_diff(json1[key], json2[key], path + key + "."))
            elif json1[key] != json2[key]:
                diffs.append(f"Difference at {path + key}: {json1[key]} != {json2[key]}")
    for key in json2.keys():
        if key not in json1:
            diffs.append(f"Missing key in json1: {path + key}")
    return "\n".join(diffs)

def compare_pdf(file1, file2):
    reader1 = PdfReader(file1)
    reader2 = PdfReader(file2)
    
    text1 = "\n".join([page.extract_text() for page in reader1.pages])
    text2 = "\n".join([page.extract_text() for page in reader2.pages])
    
    return compare_text_files(text1.splitlines(), text2.splitlines())

def compare_files(file1, file2):
    file_type1 = os.path.splitext(file1)[1].lower()
    file_type2 = os.path.splitext(file2)[1].lower()

    if file_type1 != file_type2:
        print("File types do not match. Cannot compare.")
        return

    if file_type1 in ['.txt', '.log']:
        file1_contents = get_file_contents(file1)
        file2_contents = get_file_contents(file2)
        diff = compare_text_files(file1_contents, file2_contents)

    elif file_type1 == '.csv':
        diff = compare_csv(file1, file2)

    elif file_type1 in ['.xls', '.xlsx']:
        diff = compare_excel(file1, file2)

    elif file_type1 == '.json':
        diff = compare_json(file1, file2)

    elif file_type1 == '.pdf':
        diff = compare_pdf(file1, file2)

    else:
        print(f"Unsupported file type: {file_type1}")
        return

    if diff:
        print("Differences found:")
        print(diff)
        # Output the diff in a format GitHub Actions can capture
        print(f"::set-output name=diff::{diff}")
    else:
        print("Files are identical.")

if __name__ == "__main__":
    # Replace these paths or cloud locations with your actual files
    file1 = "sample_data/one/a.csv"  # Can be s3:// or azure:// as well
    file2 = "sample_data/two/a.csv"
    
    compare_files(file1, file2)