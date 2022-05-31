import requests


def find_anchors_img_storage(image_url):
    """
    Call the function in the file denoted by the path gcf_url_file_name (should be the function executing the code to
    find the anchors), sending the url to get the image from the storage, and receives a json file in response.

    Arguments.
    image_url: String with the url of the image in the storage.

    Returns.
    response: List with the content of the json.
    """

    url = ""
    # Insert here a file which contains only the url to your cloud function
    gcf_url_file_name = "./cloud_credentials_and_links/find_anchors_url"
    with open(gcf_url_file_name, 'r') as file:
        url = file.readline()
    headers = {'Content-type': 'text/plain'}
    response = requests.post(url, headers=headers, data=image_url)

    return response.json()


def find_interesting_points_img_storage(image_url):
    """
    Call the function in the file denoted by the path gcf_url_file_name (should be the function executing the code to
    find the pints of interest), sending the url to get the image from the storage, and receives a json file in response.

    Arguments.
    image_url: String with the url of the image in the storage.

    Returns.
    response: List with the content of the json.
    """

    url = ""
    # Insert here a file which contains only the url to your cloud function
    gcf_url_file_name = "./cloud_credentials_and_links/find_interesting_points_url"
    with open(gcf_url_file_name, 'r') as file:
        url = file.readline()
    headers = {'Content-type': 'text/plain'}
    response = requests.post(url, headers=headers, data=image_url)
    return response.json()
