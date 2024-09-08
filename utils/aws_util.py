import time
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


def generate_presigned_urls(
    presigned_urls_cache: dict, bucket_name: str, folder_prefix: str, expiration=3600
):
    """
    Generates presigned URLs for all files within a specific folder in an S3 bucket.
    Checks if the presigned URLs have expired before generating new ones.

    :param bucket_name: Name of the S3 bucket.
    :param folder_prefix: The prefix (folder path) within the bucket.
    :param expiration: Time in seconds for the presigned URL to remain valid (default: 3600 seconds).
    :return: A dictionary mapping file names to their presigned URLs.
    """
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
