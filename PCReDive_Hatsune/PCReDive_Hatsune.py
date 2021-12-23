import os
from dotenv import load_dotenv

import discord

import Discord_client
import Event.Ready
import Event.Command


load_dotenv()
Discord_client.client.run(os.getenv('TOKEN'))