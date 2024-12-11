import os

import django
from telethon import TelegramClient


os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from app.models import API



apis = API.objects.all()
for api in apis:
    print(api.phone)
    client = TelegramClient(f'session/{api.id}', api_id=api.api_id, api_hash=api.api_hash,
                                system_version="4.16.30-vxCUSTOM")
    client.start(phone=api.phone, password='19097007')
    client.disconnect()