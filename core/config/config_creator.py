import os
from core.config.bot_config import BotConfig
from core.config.config_models.channel_ids import Channel_Ids
import dataclasses


def is_Y(input: str) -> bool:
    if input == "Y":
        return True
    elif input == "N":
        return False
    else:
        raise RuntimeError("Enter Y or N")


if __name__ == "__main__":
    config_file = input(
        "Please enter the path to the config file. This is just needed if you want to check new options. \
        The bot will only find the config in the default path. If you enter no path, the default path will be taken. "
    )
    config_file = config_file if config_file else "../config/configuration.json"

    reset = is_Y(input("Do you want to reset the config? [Y/N] "))
    file_exists = os.path.exists(config_file)
    if not file_exists and not reset:
        if not is_Y(input("The config file does not exists! Do you want to create a new one?")):
            exit(1)
        else:
            reset = True

    bot_config = BotConfig(config_file=config_file, update_config=not reset)

    discord_token = input("Please enter your discord token. Leave empty if the config already has an discord token: ")
    if discord_token or reset:
        bot_config.general_config.discord_token = discord_token

    riot_api = is_Y(input("Do you want to enable the riot api? You need a riot api key to do so. [Y/N] "))
    if riot_api:
        riot_token = input("Please enter your riot api key. Leave empty to not change the key: ")
        if not riot_token and not bot_config.general_config.riot_token:
            print("No riot api key. Disable riot api")
            riot_api = False
        else:
            bot_config.general_config.riot_api = True
            bot_config.general_config.riot_token = riot_token

    while True:
        new_guild_id_str = input("Please enter a guild id. Enter nothing to stop: ")
        if not new_guild_id_str:
            break
        new_guild_id = int(new_guild_id_str)
        if bot_config.check_if_guild_exists(new_guild_id):
            if is_Y(input("Guild does already exist! Do you want to reset the settings of this guild?")):
                bot_config.remove_guild_config(new_guild_id)
            else:
                continue

        bot_config.add_new_guild_config(new_guild_id)
        guild_config = bot_config.get_guild_config(new_guild_id)

        while True:
            command_prefix = str(
                input("Please insert a command string to call a command. Leave empty to leave unchanged: ")
            )
            if command_prefix == "<":
                print("Sorry this is forbidden by Discord...")
            else:
                break
        if command_prefix:
            guild_config.unsorted_config.command_prefix = command_prefix

        if bot_config.general_config.riot_api:
            guild_config.unsorted_config.riot_region = str(
                input("Please insert your riot region. Example for Europe west: 'euw1': ")
            )

        everyone_id = int(
            input("Please insert the id of the role that belongs to everyone. Leave empty to leave unchanged: ")
        )
        guest_id = int(
            input(
                "Please insert the id of the role that belongs to guests of the server. \
                Leave empty to leave unchanged: "
            )
        )
        member_id = int(
            input(
                "Please insert the id of the role that belongs to members of the server. \
                Leave empty to leave unchanged: "
            )
        )
        admin_id = int(
            input("Please insert the id of the role that can configure the bot. Leave empty to leave unchanged: ")
        )

        if everyone_id:
            guild_config.unsorted_config.everyone_id
        if guest_id:
            guild_config.unsorted_config.guest_id
        if member_id:
            guild_config.unsorted_config.member_id
        if admin_id:
            guild_config.unsorted_config.admin_id

        while True:
            game_name_short = input(
                "Please enter a short name for a game (Example: 'LoL' for 'League of Legends'). \
                Enter nothing to stop: "
            )
            if not game_name_short:
                break
            elif guild_config.game_exists(game_name_short):
                print("That game already exists!")
                continue
            else:
                long_name = input("\tPlease enter the full name for the game: ")
                role_id = int(input("\tPlease enter the id of the discord role that belongs to the game: "))
                emoji_id = int(input("\tPlease enter the id of the discord emoji that belongs to the game: "))
                category_id = int(input("\tPlease enter the id of a channel (category) of this game. "))
                cog_path = input("\tPlease enter the path to a cog of this game. Leave empty if there is no cog: ")
                cog_path = cog_path if cog_path else None
                guild_config.add_game(
                    game=game_name_short,
                    long_name=long_name,
                    role_id=role_id,
                    emoji=emoji_id,
                    category_id=category_id,
                    cog=cog_path,
                )
                print(long_name, "was added to the guild config")
        print("")

        if not guild_config.command_has_config("purge"):
            guild_config.add_command_config(command_name="purge", enabled=True, allowed_from_roles=("admin_id",))

        while True:
            command = input("Please enter a command that should be configured: ")
            if not command:
                break
            elif guild_config.command_has_config(command):
                if is_Y(
                    input(
                        "The command already has a config. \
                        Do you want to delete the config and create a new one? [Y/N] "
                    )
                ):
                    guild_config.remove_command_config(command)
                else:
                    continue
            game_config = {}

            disabled = is_Y(input("Do you want to disable this command? [Y/N] "))
            if disabled:
                game_config["enabled"] = False
            else:
                game_config["enabled"] = True

                print("For the next options, you can leave the option empty to not use the option.")

                valid_channel_names = [field.name for field in dataclasses.fields(Channel_Ids)]
                channel_names = input(
                    f"The config groups some channels. \
                    Enter the names for the channel groups in that the command should be allowed. \
                    Seperate names by a space character. Valid names are {', '.join(valid_channel_names)}. \
                    Invalid names are ignored without a warning: "
                ).split(" ")
                allowed_in_channels = [
                    str(channel) for channel in channel_names if str(channel) in valid_channel_names
                ]
                if allowed_in_channels:
                    game_config["allowed_in_channels"] = allowed_in_channels

                allowed_in_channel_ids = [
                    int(id) for id in input("Enter additional ids of the channels in that the command is allowed: ")
                ]
                if allowed_in_channel_ids:
                    game_config["allowed_in_channel_ids"] = allowed_in_channel_ids

                allowed_from_roles = [
                    str(role)
                    for role in input(
                        "The config also groups some roles. \
                        Enter the names for the channel groups in that the command should be allowed. \
                        Valid names are admin_id, member_id, guest_id, everyone_id and the short name of a game: "
                    )
                ]
                if allowed_from_roles:
                    game_config["allowed_from_roles"] = allowed_from_roles

                allowed_from_role_ids = [int(id) for id in input("Enter ids of the roles that the command can use: ")]
                if allowed_from_role_ids:
                    game_config["allowed_from_role_ids"] = allowed_from_role_ids

            guild_config.add_command_config(command_name=command, **game_config)
            print("Command added!")

        print("\nFinished with guild config\n")

    bot_config.write_config_to_file()

    print(
        f"Config was written to:'{bot_config.general_config.config_file}'. \
        You can configure the bot even more  in this file."
    )
