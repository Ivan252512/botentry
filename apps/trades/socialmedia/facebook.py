import requests

from django.conf import settings

class Facebook:
    def __init__(self):
        self.page_id = settings.FACEBOOK_PAGE_ID
        self.access_token = settings.FACEBOOK_ACCESS_TOKEN
        
    def post_photo(self, _message, _path_photo):
        url = f"https://graph.facebook.com/{self.page_id}/photos?url={_path_photo}&message={_message}&access_token={self.access_token}"

        payload={}
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload)
        
        return response.json()

    def test_post_photo(self):
        return self.post_photo("Prueba desde la api", "https://botentry.s3.us-west-2.amazonaws.com/graphics/BTCBUSD/4h/not_ai/01_02_2022_20_30_53.jpg")