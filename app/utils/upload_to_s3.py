import boto3
import uuid
import os
import dotenv
dotenv.load_dotenv()
s3 = boto3.client(
  "s3",
  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
  region_name=os.getenv("AWS_REGION"),
)

BUCKET_NAME = os.getenv("AWS_S3_BUCKET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5000")
def upload_file_to_s3(file, folder='uploads', public=True):
    if not file:
        return None

    file_extension = file.filename.split(".")[-1]
    key = f"{folder}/{uuid.uuid4()}.{file_extension}"

    s3.upload_fileobj(
        file,
        BUCKET_NAME,
        key,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )

    return key


def get_public_url(key):
    return f"{FRONTEND_URL}/{key}"

def generate_presigned_url(key, expires=300):
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": key,
        },
        ExpiresIn=expires
    )


