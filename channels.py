import asyncio
import datetime
import os
import random
import time

import telethon
from django.utils import timezone
from telethon import types
from telethon.sync import TelegramClient
from telethon.tl.functions import messages, channels, users, stories, account, photos
from telethon import functions, types
from telethon import functions

import django

import avatar

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from app.models import API, Orders, WaveTime


async def create_new_order(client, url):
    try:
        order = Orders.objects.get(url=url)
    except Exception:
        order = Orders.objects.create(
            url=url,
            gender=3,
            start=timezone.now(),
            next_action_time=timezone.now(),
            end=timezone.now() + datetime.timedelta(days=30)
        )
        order.apis.add(client)
    else:
        if client not in order.apis.all():
            order.apis.add(client)


async def read_messages_and_set_reactions(client, entity, client_data, limit=2):
    offset_msg = 0
    limit_msg = limit
    messages = await client.get_messages(entity, limit)
    messages_id = [message.id for message in messages]
    result = await client(functions.messages.GetMessagesViewsRequest(
        peer=entity,
        id=messages_id,
        increment=True
    ))
    for msg in messages:
        if random.randint(0, 4) == 1:
            try:
                try:
                    a = random.randint(0, len(msg.reactions.results) - 1)
                    emotion = msg.reactions.results[a].reaction.emoticon
                except Exception:
                    emotion = '❤️'
                try:
                    await client(messages.SendReactionRequest(
                        peer=entity,
                        msg_id=msg.id,
                        reaction=[types.ReactionEmoji(emoticon=emotion)]
                    ))
                except Exception as e:
                    pass
            except Exception as e:
                pass
        if random.randint(0, 9) == 2:
            a = True
            if msg.message:
                for link in msg.message.split():
                    if 'https://t.me/' in link:
                        await create_new_order(client_data, link)
                for entity in msg.entities:
                    if 'https://t.me/' in entity.url:
                        await create_new_order(client_data, entity.url)


async def subscribe_privat_channel(client, hash):
    try:
        await client(messages.ImportChatInviteRequest(hash))
    except Exception as e:
        print(f'subscribe_privat_channel: {e}')


async def subscribe_public_channel(entity, client):
    try:
        a = await client(functions.channels.JoinChannelRequest(channel=entity))
    except Exception as e:
        print(f'subscribe_public_channel: {e}')


async def subscribe_on_channels(client, channel_url):
    try:
        entety = await client.get_entity(channel_url)
        await subscribe_public_channel(channel_url, client)
    except Exception as ex:
        await subscribe_privat_channel(client, channel_url[14:])


async def activate_user(api):
    client = TelegramClient(f'session/{api.id}', api_id=api.api_id, api_hash=api.api_hash,
                            system_version="4.16.30-vxCUSTOM", lang_code='ru', system_lang_code='ru')
    while True:
        try:
            await client.start(phone=api.phone, password='19097007')
            try:
                await avatar.start(api=api, client=client)
            except Exception:
                pass
            try:
                await client(functions.account.UpdateStatusRequest(
                    offline=False
                ))
                return client
            except Exception:
                pass
        except Exception as e:
            time.sleep(10)


async def channels(order, wave_time):
    start = order.start.timestamp()
    now = timezone.now().timestamp()
    if start <= now:
        count = len(order.apis.all())
        if order.number_wave == 0:
            sleep_time = wave_time.first
            count = int(count * 0.6)
        elif order.number_wave == 1:
            sleep_time = wave_time.second
            count = int(count * 0.9)
        elif order.number_wave >= 2:
            sleep_time = wave_time.third
        no_subscribe = order.apis.all()[order.subscribe: count]
        subscribe = order.apis.all()[:order.subscribe]
        action_time = order.next_action_time
        now_time = timezone.now()
        try:
            nm = now_time.timestamp() - action_time.timestamp()
        except Exception:
            order.action_time = timezone.now()
            order.save()
        if (not order.next_action_time or nm >= 0) and len(no_subscribe) > 0:
            user = no_subscribe[0]
            try:
                client = await activate_user(user)
            except Exception as e:
                pass
            await subscribe_on_channels(client, order.url)
            order.subscribe += 1
            print('Подписался')
            order.next_action_time = timezone.now() + datetime.timedelta(seconds=1)
            if order.subscribe == count:
                order.number_wave += 1
            order.save()
            see_post = 3
            if random.randint(0, 100) <= 50:
                see_post += 2
            if random.randint(0, 100) <= 25:
                see_post += 2
            if random.randint(0, 100) <= 10:
                see_post += 2
            try:
                entity = await client.get_entity(order.url)
                await read_messages_and_set_reactions(client, entity, user, limit=see_post)
            except Exception as ex:
                pass
            await client.disconnect()
        if subscribe:
            for user in subscribe:
                client = await activate_user(user)
                try:
                    entity = await client.get_entity(order.url)
                    await read_messages_and_set_reactions(client, entity, user)
                except Exception as ex:
                    pass
                # time.sleep(random.randint(1, 2))
                await client.disconnect()


async def bot(bot_url, client):
    await client.send_message(entity=bot_url, message='/start')
    time.sleep(1)
    messages = await client.get_messages(bot_url)
    for entity in messages[0].entities:
        try:
            url = entity.url
            if url[-3:] == 'bot':
                await bot(url, client)
            else:
                await subscribe_on_channels(client, url)
        except Exception:
            pass
    for row in messages[0].reply_markup.rows:
        for button in row.buttons:
            try:
                url = button.url
                if url[-3:] == 'bot':
                    await bot(url, client)
                else:
                    await subscribe_on_channels(client, url)
            except Exception:
                try:
                    button.data
                except Exception:
                    pass
                else:
                    text = button.text
    try:
        await messages[0].click(text=text)
    except Exception:
        pass
    await client.disconnect()


async def leave_channel(order):
    if order.subscribe > 0:
        api = order.apis.all()[order.subscribe - 1]
        client = await activate_user(api)
        try:
            entety = await client.get_entity(order.url)
            await client(functions.channels.LeaveChannelRequest(channel=entety.id))
        except Exception as ex:
            print(f'leave_channel {ex}')
        order.subscribe -= 1
        order.save()
    else:
        order.delete()


async def start():
    while True:
        wave_time = WaveTime.objects.all()[0]
        for order in Orders.objects.all():
            if order.url[-3:] == 'bot':
                if timezone.now().timestamp() >= order.end.timestamp():
                    order.delete()
                else:
                    for api in order.apis.all():
                        client = await activate_user(api)
                        await bot(order.url, client)
            else:
                if timezone.now().timestamp() >= order.end.timestamp():
                    await leave_channel(order)
                else:
                    await channels(order, wave_time)
        time.sleep(5)
