from uuid import uuid4
import discord
import yaml
import logging
import json
import requests
from pathlib import Path
import privatebinapi



logging.basicConfig(level=logging.INFO)

# read the config
client = discord.Client()
source_folder = Path(__file__).parent
with open(source_folder / "config.yml", 'rb') as configstream:
    config = yaml.safe_load (configstream)
    token = config.get('token')
    uri = config.get('uri')
    platform = config.get('platform')
    bot_message = config.get('bot_message')
cache_folder = source_folder / 'cache'

async def save_to_cache(attachment):
    local_file = cache_folder / (str(uuid4())+".txt")
    try:
        await attachment.save(local_file)
        logging.info(attachment.filename+' was saved!')
        local_file_content = ""
        with open(local_file, 'r') as local_file_stream:
            local_file_content = local_file_stream.read()
        try:
            local_file.unlink()
        except:
            logging.error(attachment.filename+' could not be deleted.')
        finally:
            return local_file_content
    except: 
        logging.error(attachment.filename+' could not be saved.')
    
    return ""

def upload_to_bin (content):
    if platform=='hastebin':
        response = requests.post(uri+'documents', data=content)
        response_content =json.loads(response.text)['key']

        logging.info ('api response: '+str(response.text))
        if len(response_content)<=10:
            return (uri+response_content),True
        else:
            return "",False
    if platform=='privatebin':
        response = privatebinapi.send(uri, text=content)
        if response['status']==0:
            return response['full_url'],True
        else:
            return "", False
    return "Wrong configuration!",False
def clear_cache():
    cache_folder.rmdir
    cache_folder.mkdir(parents=True, exist_ok=True)
    return True


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if len(message.attachments)>0:
        for attachment in message.attachments:
            if attachment.content_type.startswith('text'):
                attachment_content = await save_to_cache(attachment)
                if attachment_content!="":
                        link,success = upload_to_bin(attachment_content)
                        if (success):
                            await message.channel.send(bot_message+link, reference=message, mention_author=False)
        return

clear_cache()
client.run(token)