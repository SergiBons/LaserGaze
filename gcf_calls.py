import requests


def process_image_on_storage(image_url):
    url = ""
    # Insert here a file which contains only the url to your cloud function
    gcf_url_file_name = "/home/lasergaze/Desktop/Repo/cloud_credentials_and_links/gcf_url"
    with open(gcf_url_file_name, 'r') as file:
        url = file.readline()
    headers = {'Content-type': 'text/plain'}
    response = requests.post(url, headers=headers, data=image_url)

    return response.json()
