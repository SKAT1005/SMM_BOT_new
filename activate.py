import datetime
import json
import os
import random

import django
from django.utils import timezone

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from app.models import API

from telethon import TelegramClient

with open('1.json', 'r') as file:
    a = json.load(file)
    for i in a:
        try:
            print(f'{i["fields"]["phone"]} | {i["pk"]} | {i["fields"]["number"]}')
            client = TelegramClient(f'session/{i["pk"]}', api_id=i['fields']["api_id"], api_hash=i['fields']['api_hash'],
                                    system_version="4.16.30-vxCUSTOM")
            client.start(password='19097007', phone=i['fields']['phone'], )
            client.disconnect()
            next_update_photo_time = timezone.now() + datetime.timedelta(
                minutes=random.randint(1 * 24 * 60, 4 * 24 * 60))
            api, _ = API.objects.get_or_create(phone=i['fields']['phone'], gender=i['fields']['gender'],
                                               username=i['fields']['username'], api_id=i['fields']['api_id'],
                                               api_hash=i['fields']['api_hash'])
            if _:
                api.next_update_photo_time = next_update_photo_time
                api.save()
        except Exception:
            print(f'Ошибка с номером {i["fields"]["number"]}')
