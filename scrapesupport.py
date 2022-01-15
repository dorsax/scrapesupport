from uuid import uuid4
import discord
import yaml
import logging
import json
import requests
from pathlib import Path



logging.basicConfig(level=logging.INFO)

# read the config
client = discord.Client()
source_folder = Path(__file__).parent
with open(source_folder / "config.yml", 'rb') as configstream:
    config = yaml.safe_load (configstream)
    token = config.get('token')
    uri = config.get('hastebin_uri')
    bot_message = config.get('bot_message')
cache_folder = source_folder / 'cache'

async def save_to_cache(attachment):
    local_file = cache_folder / (str(uuid4())+".txt")
    try:
        await attachment.save(local_file)
        logging.info(attachment.filename+' was saved!')
        local_file_content = ""
        with open(local_file, 'rb') as local_file_stream:
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
                        post_data = {
                            "api_paste_code" : attachment_content,
                            "api_option" : "paste",
                            "api_dev_key" : pastebin_key,
                            "api_paste_name" : attachment.filename
                        }
                        response = requests.post(uri+'documents', data=attachment_content)
                        response_content =json.loads(response.text)['key']

                        logging.info ('api response: '+str(response.text))
                        if (len(response_content)<=10):
                            await message.channel.send(bot_message+uri+response_content, reference=message, mention_author=False)
        return

clear_cache()
client.run(token)