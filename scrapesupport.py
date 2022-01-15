import discord
import yaml
import os
import logging
import requests
import re

logging.basicConfig(level=logging.INFO)

client = discord.Client()
source_folder=os.path.dirname(os.path.realpath(__file__))+os.path.sep
configstream = open(source_folder+"config.yml", 'r')
config = yaml.safe_load (configstream)
token = config.get('token')
pastebin_key = config.get('pastebin_key')

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
                was_error = False
                local_file=source_folder +attachment.filename
                try:
                    await attachment.save(local_file)
                    logging.info(attachment.filename+' was saved!')
                except: 
                    logging.error(attachment.filename+' could not be saved.')
                    was_error = True
                
                if not(was_error):
                    with open(local_file, 'rb') as local_file_stream:

                        post_data = {
                            "api_paste_code" : local_file_stream.read(),
                            "api_option" : "paste",
                            "api_dev_key" : pastebin_key,
                            "api_paste_name" : attachment.filename
                        }
                        response = requests.post('https://pastebin.com/api/api_post.php', data=post_data)
                        response_content = re.sub(r"b'(.*)'",r"\1",str(response.content)) # response.content is byte, thats why the format is b'<actual content>' and needs to be stripped...

                        logging.info ('api response: '+str(response_content))
                        if (response_content.startswith('https://pastebin.com')):
                            await message.channel.send('For better support on mobile, your file was uploaded to '+response_content)
                
        # await message.channel.send('Message with attachments detected!')
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


client.run(token)