import os
import requests
from supabase import create_client, Client
import json
supabase: Client = create_client('http://82.146.56.214:8000', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE')

def get_n_send():
    response = supabase.table('notifications').select("*").execute()
    data_res = json.loads(response.json())['data']

    headers = {
        "accept": "application/json",
        "Authorization": "MmUwYWZmMjQtMjk4Yy00ZTk1LWEzNmItNDE0YmZkODlhY2Ex",
        "content-type": "application/json"
    }

    url = "https://onesignal.com/api/v1/notifications"
    
    for noti in data_res:
        payload = {
            "include_subscription_ids": ['9e57e587-166d-86d7-6b19-918329196a17'],
            "contents": {
                "en": noti['description'],
                "ru": "Иначе..."
            },
            "app_id": "bae4b484-acfa-418b-b5f7-c74da3ffe78b"
        }

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)


if __name__ == "__main__":
    get_n_send()