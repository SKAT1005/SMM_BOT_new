import asyncio
import datetime
import os
import random
import time

from django.utils import timezone
from telethon import TelegramClient
from telethon.tl.functions import photos

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from app.models import API
async def update_my_photo(client, api):
    await client.download_profile_photo('me', f'profile_photos/user_{api.id}.jpg')
    await client(photos.DeletePhotosRequest(await client.get_profile_photos('me')))
    await client(photos.UploadProfilePhotoRequest(file=await client.upload_file(f'profile_photos/user_{api.id}.jpg')))


async def update_donor_photo(client, api):
    try:
        a = await client.get_profile_photos(api.username.replace('@', ''))
        if str(a[0].id) == api.last_photo_id:
            api.try_count += 1
            api.save()
            if api.try_count >= random.randint(4, 6):
                await client.download_media(random.choice(a), f'profile_photos/user_{api.id}.jpg')
                await client(photos.DeletePhotosRequest(await client.get_profile_photos('me')))
                await client(photos.UploadProfilePhotoRequest(file=await client.upload_file(f'profile_photos/user_{api.id}.jpg')))
        else:
            api.try_count = 0
            api.save()
            await client.download_profile_photo(api.username.replace('@', ''), f'profile_photos/user_{api.id}.jpg')
            await client(photos.DeletePhotosRequest(await client.get_profile_photos('me')))
            await client(photos.UploadProfilePhotoRequest(file=await client.upload_file(f'profile_photos/user_{api.id}.jpg')))
    except Exception as ex:
        await update_my_photo(client, api)



async def start(api, client):
    if timezone.now().timestamp() >= api.next_update_photo_time.timestamp() and api.username not in ['', '-']:
            await update_donor_photo(client, api)
            next_update_photo_time = timezone.now() + datetime.timedelta(minutes=random.randint(6*24*60,8*24*60))
            api.next_update_photo_time = next_update_photo_time
            api.save(update_fields=['next_update_photo_time'])
