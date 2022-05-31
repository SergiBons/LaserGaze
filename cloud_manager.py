from gcf_calls import *
from storage_files import upload_to_bucket
from urllib.parse import urlparse


def send_image_find_anchors(file_path):
    """
    Uploads an image to storage, and send it's uri to the anchor recognition cloud function in order to get back if
    the anchors were found in that image, and if they were, also get back their position inside the image.

    Arguments.
    file_path: String with the path to the image to process.

    Returns.
    anchor_1_found: Boolean, True if the anchor 1 have been found, False otherwise.
    anchor_2_found: Boolean, True if the anchor 2 have been found, False otherwise.
    anchor_1: Map of 2 components, 'x' and 'y' each containing a float that represents the normalized location of the
                anchor 1 in the image.
    anchor_2: Map of 2 components, 'x' and 'y' each containing a float that represents the normalized location of the
                anchor 2 in the image.
    """

    image_url = upload_to_bucket("test.jpg", file_path)
    uri = urlparse(image_url).path
    url = "gs:/" + uri
    resposta = find_anchors_img_storage(url)

    anchor_1_found = False
    anchor_2_found = False
    anchor_1 = None
    anchor_2 = None

    for key in resposta:
        if key['anchor'] == 1:
            anchor_1_found = True
            anchor_1 = {'x': 0, 'y': 0}
            anchor_1['x'] = key['normalized_position_x']
            anchor_1['y'] = key['normalized_position_y']
        elif key['anchor'] == 2:
            anchor_2_found = True
            anchor_2 = {'x': 0, 'y': 0}
            anchor_2['x'] = key['normalized_position_x']
            anchor_2['y'] = key['normalized_position_y']

    return anchor_1_found, anchor_2_found, anchor_1, anchor_2


def send_image_find_interesting_points(file_path):
    """
    Uploads an image to storage, and send it's uri to the find_interesting_points cloud function in order to get back
    100 points of interest found in the image.

    Arguments.
    file_path: String path to the image to process.

    Returns.
    resposta: List of 100 elements with a map each which contains 2 elements 'x' and 'y' which in turn contains a float
                that represents the absolute position of the points of interest in the image.
    """

    image_url = upload_to_bucket("test.jpg", file_path)
    uri = urlparse(image_url).path
    resposta = find_interesting_points_img_storage(uri)

    return resposta


def send_image_find_anchors_and_find_interesting_points(file_path, anchor_1_already_found, anchor_2_already_found):

    image_url = upload_to_bucket("test.jpg", file_path)
    uri = urlparse(image_url).path
    url = "gs:/" + uri
    
    anchor_1_found = False
    anchor_2_found = False
    anchor_1 = None
    anchor_2 = None
    
    if not anchor_1_already_found and not anchor_2_already_found:
        resposta = find_anchors_img_storage(url)
        for key in resposta:
            if key['anchor'] == 1:
                anchor_1_found = True
                anchor_1 = {'x': 0, 'y': 0}
                anchor_1['x'] = key['normalized_position_x']
                anchor_1['y'] = key['normalized_position_y']
            elif key['anchor'] == 2:
                anchor_2_found = True
                anchor_2 = {'x': 0, 'y': 0}
                anchor_2['x'] = key['normalized_position_x']
                anchor_2['y'] = key['normalized_position_y']

    resposta = find_interesting_points_img_storage(uri)

    return anchor_1_found, anchor_2_found, anchor_1, anchor_2, resposta

def upload_points(file_path):
    """
    Uploads a file containing the 3D points generated to the storage.

    Arguments.
    file_path: String path to the file to upload.

    """
    upload_to_bucket("points.txt", file_path, points=True)