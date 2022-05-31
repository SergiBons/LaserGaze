from google.cloud import storage


def upload_to_bucket(blob_name, path_to_file, points=False):
    """
    Upload data to a bucket

    Arguments.
    blob_name: String with the name to save the image with in the storage.
    file_path: String with the path to the image to upload.
    points: Boolean denoting if we want to upload an image to the img folder, or a file with 3D points to
            the point_cloud folder.

    Returns.
    public_url: String with the url to go to the image in the storage.
    """

    # Explicitly use service account credentials by specifying the private key
    # file.
    # Insert here your account credentials file
    credentials_file_path = './cloud_credentials_and_links/anchor-recognition-0810bc18ca59.json'
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
    """
    Download data from the lasergaze-data bucket

    Arguments.
    file_name: String with the name of the image in the storage.
    points: Boolean denoting if we want to download an image from the img folder, or a file with 3D points from
            the points folder.

    """

    # Initialise a client
    # Insert here your account credentials file
    credentials_file_path = './cloud_credentials_and_links/anchor-recognition-0810bc18ca59.json'
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
