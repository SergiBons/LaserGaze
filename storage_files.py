from google.cloud import storage


def upload_to_bucket(blob_name, path_to_file, points=False):
    """ Upload data to a bucket """

    # Explicitly use service account credentials by specifying the private key
    # file.
    # Insert here your account credentials file
    credentials_file_path = '/home/lasergaze/Desktop/Repo/cloud_credentials_and_links/anchor-recognition-0810bc18ca59.json'
    storage_client = storage.Client.from_service_account_json(credentials_file_path)

    # print(buckets = list(storage_client.list_buckets())

    bucket = storage_client.get_bucket('lasergaze-data')

    if points == True:
        blob = bucket.blob("point_cloud/"+blob_name)
    else:
        blob = bucket.blob("img/"+blob_name)

    blob.upload_from_filename(path_to_file)

    # returns a public url
    return blob.public_url


def download_from_bucket(file_name, points=False):
    """ Download data from the lasergaze-data bucket """

    # Initialise a client
    # Insert here your account credentials file
    credentials_file_path = '/home/lasergaze/Desktop/Repo/cloud_credentials_and_links/anchor-recognition-0810bc18ca59.json'
    storage_client = storage.Client.from_service_account_json(credentials_file_path)

    # Create a bucket object for our bucket
    bucket = storage_client.get_bucket('lasergaze-data')

    # Create a blob object from the filepath
    if points == True:
        path = "point_cloud/"+file_name
    else:
        path = "img/"+file_name

    blob = bucket.blob(path)

    # Download the file to a destination
    blob.download_to_filename(file_name)



## Example of usage (upload_to_bucket)

# blob = 'tpose.jpg' # Name to save the uploaded file on the cloud
# path = 'C:/Users/megag/OneDrive/Escritorio/UAB/3er/S.M/Projecte/tpose.jpg' # Path to the file to be uploaded

# url = upload_to_bucket(blob,path) # URL of the uploaded file

## Example of usage (download_from_bucket)

# file = "tpose.jpg"

# download_from_bucket(file)
