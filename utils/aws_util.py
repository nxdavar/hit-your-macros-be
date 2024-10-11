import time

import boto3

"""
Generates presigned URLs for all files within a specific folder in an S3 bucket.
Checks if the presigned URLs have expired before generating new ones.

:param bucket_name: Name of the S3 bucket.
:param folder_prefix: The prefix (folder path) within the bucket.
:param expiration: Time in seconds for the presigned URL to remain valid (default: 3600 seconds).
:return: A dictionary mapping file names to their presigned URLs.
"""


def generate_presigned_urls(
    presigned_urls_cache: dict,
    bucket_name: str,
    folder_prefix: str,
    expiration=3600,
    keyword=None,
):

    s3_client = boto3.client("s3")

    try:
        # List objects within the specified folder
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

        if "Contents" not in response:
            print("No files found in the specified folder.")
            return {}

        # Generate presigned URLs for each object
        current_time = int(time.time())
        for obj in response["Contents"]:
            file_key = obj["Key"]
            print("file key: ", file_key)

            # Check if a valid presigned URL already exists in the cache
            if file_key in presigned_urls_cache:
                cached_url, expiry_time = presigned_urls_cache[file_key]
                if current_time < expiry_time:
                    # Presigned URL is still valid, skip generation
                    print(f"Using cached URL for {file_key}")
                    continue

            # Generate a new presigned URL
            presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": file_key},
                ExpiresIn=expiration,
            )
            # Store the presigned URL and its expiration time in the cache
            expiry_time = current_time + expiration
            presigned_urls_cache[file_key] = (presigned_url, expiry_time)
            print(f"Generated new URL for {file_key}")

        return {file_key: url for file_key, (url, _) in presigned_urls_cache.items()}

    except boto3.exceptions.S3UploadFailedError as e:
        print(f"Error: {e}")
        return {}


"""
Generates a presigned url for a specific file in the S3 bucket that contains param keyword in its name.
:param bucket_name: Name of the S3 bucket.
:param keyword: Keyword to search for in the file name.
:param expiration: Time in seconds for the presigned URL to remain valid (default: 3600 seconds).
:return: A presigned URL for the file containing the keyword in its name.
"""


def generate_presigned_url_for_file_with_keyword(
    bucket_name: str, keyword: str, folder_prefix: str, expiration=3600
):
    s3_client = boto3.client("s3")

    try:
        # List objects in the specified bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

        if "Contents" not in response:
            print("No files found in the specified folder.")
            return {}

        # Find the first file with the specified keyword in the file name
        matching_files = [
            obj["Key"] for obj in response["Contents"] if keyword in obj["Key"]
        ]

        if not matching_files:
            print(
                f"No files found in bucket '{bucket_name}' containing the keyword '{keyword}'."
            )
            return None

        # Use the first matching file (modify as needed to handle multiple matches)
        file_key = matching_files[0]
        print(f"Found matching file: {file_key}")

        # Generate a presigned URL for the matching file
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": file_key},
            ExpiresIn=expiration,
        )
        print(f"Generated URL for {file_key}: {presigned_url}")

        return presigned_url

    except boto3.exceptions.S3UploadFailedError as e:
        print(f"Error: {e}")
        return None
