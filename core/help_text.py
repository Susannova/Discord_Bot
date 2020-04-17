""" Used for help texts """

class Help_Text(object):
    """This class contains the brief and long help textes for the commands"""
    def __init__(self, command, text):
        self.brief = 'Usage: ``' + brief + '``',
        self.long = command + '\n' + text

link_help_text = Help_Text(
    '!link summonername',
    'Links your discord account with your Riot-Account on this server. To unlink, use ``!unlink``.'
    )

unlink_help_text = Help_Text(
    '!unlink',
    'Unlinks your discord account from your Riot-Account on this server. To link again, use ``!link summonername``.'
    )

leaderboard_help_text = Help_Text(
    '!leaderboard',
    'Prints the LoL leaderboard for users in this channels. To link your Riot Account, use ``link summonername``'
    )

create_channel_help_text = Help_Text(
    '!create-channel ( text | (voice [user_limit]) ) name',
    'Benutze dieses Command um einen Channel zu erstellen der für 12h aktiv ist und danach gelöscht wird. Der Channel ist in der Kategorie TEMPORARY CHANNELS zu finden.'
    )