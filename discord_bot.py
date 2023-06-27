"""
Main module.

Start and define the Discord Bot (`KrautBot`).
"""
import logging
import os
import sys

logging.basicConfig(
    filename="log/log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("main")

os.environ["TZ"] = "Europe/Berlin"

import discord

from core.kraut_bot import KrautBot

discord.voice_client.VoiceClient.warn_nacl = False


if __name__ == "__main__":
    bot = KrautBot()
    bot.run()
    bot.state.write_state_to_file()
    bot.config.write_config_to_file()
    print("Global state and Config saved to file.")
    logger.info("Global state and Config saved to file.")
    logger.info("End")
    sys.exit(bot.exit_status)
