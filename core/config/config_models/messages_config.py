import dataclasses


@dataclasses.dataclass
class Messages_Config:
    """Configuration data of the messages from the bot."""

    date_format: str = "{day}.{month}."
    auto_dm_creator: str = "{player} hat auf dein Play-Request reagiert: {reaction} "
    auto_dm_subscriber: str = "{player} hat auch auf das Play-Request von {creator} reagiert: {reaction} "
    play_now: str = (
        "{role_mention}\n{creator} spielt **__jetzt gerade__** **{game}** und sucht noch nach weiteren Spielern!"
    )
    play_at: str = "{role_mention}\n{player} will **{game}** spielen. Kommt {date_str} um **__{time}__** Uhr online!"
    players_needed: str = "Es werden noch {player_needed_num} weitere Spieler benötigt."
    play_at_date: str = "am **__{date}__**"

    play_request_reminder: str = "REMINDER: Der abonnierte Play-Request geht in {minutes} Minuten los!"

    bans: str = (
        "If you want to receive the best bans"
        "for the scouted team copy the following Command: \n"
        "{command_prefix}bans {team}"
    )

    team_header: str = "\n**__Teams:__**\n"
    team_1: str = "Team 1:\n"
    team_2: str = "\nTeam 2:\n"

    patch_notes_formatted: str = "{role_mention}\nEin neuer Patch ist da: {patch_note}"
    patch_notes: str = "https://euw.leagueoflegends.com/en-us/news/game-updates/patch-{0}-{1}-notes/"

    game_selector: str = (
        "@everyone\nWähle hier durch das Klicken auf eine Reaktion aus"
        "zu welchen Spielen du Benachrichtungen erhalten willst!"
    )

    highlight_leaderboard_description: str = "Vote for the best highlights in {highlight_channel_mention}."
    highlight_leaderboard_footer: str = "Only the last {limit} highlights can be taken in account."
    place: str = "Place"

    # deprecated but need to be manually deleted from config before deleting from this class
    create_internal_play_request: str = ""
    clash_create: str = ""
    clash_full: str = ""
