from gcf_calls import process_image_on_storage
from storage_files import upload_to_bucket
from urllib.parse import urlparse


def send_image_find_anchors(file_path):
    image_url = upload_to_bucket("test.jpg", file_path)
    path = urlparse(image_url).path
    uri = "gs:/" + path
    resposta = process_image_on_storage(uri)
    
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
            print("Ancora 1 trobada")
        elif key['anchor'] == 2:
            anchor_2_found = True
            anchor_2 = {'x': 0, 'y': 0}
            anchor_2['x'] = key['normalized_position_x']
            anchor_2['y'] = key['normalized_position_y']
            print("Ancora 2 trobada")

    return anchor_1_found, anchor_2_found, anchor_1, anchor_2
