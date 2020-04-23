""" Used for help texts """

from core import consts

class HelpText(object):
    """This class contains the brief and long help textes for the commands"""
    def __init__(self, text, brief, usage = ''):
        self.text = text
        self.brief = brief
        self.usage = usage

create_team_HelpText = HelpText(
    'Erstellt zwei zufällige Teams aus den Mitgliedern des Voice Channels und gegebenfalls weiteren, angegebene Spielern. Mit der Option \'mv\' werden die Spieler automatisch in die entsprechende Channels bewegt.',
    'Erstellt zwei zufällige Teams',
    '[mv] [names]'
)

link_HelpText = HelpText(
    'Links your discord account with your Riot-Account on this server. To unlink, use ``!unlink``.',
    'Links Riot account',
    'summonername'
    )

unlink_HelpText = HelpText(
    'Unlinks your discord account from your Riot-Account on this server. To link again, use ``!link summonername``.',
    'Unlinks Riot account'
    )

leaderboard_HelpText = HelpText(
    'Prints the LoL leaderboard for users in this server. To link your Riot account, use ``link summonername``',
    'Prints LoL leaderboard'
    )

create_channel_HelpText = HelpText(
    'Benutze dieses Command um einen Channel zu erstellen der für 12h aktiv ist und danach gelöscht wird. Der Channel ist in der Kategorie TEMPORARY CHANNELS zu finden.',
    'Creates a temporary channel',
    '( text | voice ) name [voice_chat_user_limit]'
    )

play_HelpText_long = 'und benachrichtigt alle User, die dieses Spiel auf dem Server aboniert haben. Auf die Anfrage kann mit ' + ':fill:' + ' und ' + consts.EMOJI_PASS + ' reagiert werden, wodurch der Ersteller und bereits beigetretene Spieler eine Benachrichtigung erhalten.'

play_HelpText = HelpText(
    'Erstellt eine Spielanfrage ' + play_HelpText_long + ' Der Ersteller und die Spieler bekommen kurz vor Beginn des Spieles eine Nachricht.',
    'Erstellt eine Spielanfrage',
    'game (\'now\' | time)'
)

create_clash_HelpText = HelpText(
    'Erstellt eine Clash-Anfrage für das gegebene Datum ' + play_HelpText_long,
    'Erstellt eine Clash-Anfrage',
    'date'
)
