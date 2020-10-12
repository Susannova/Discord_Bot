""" Used for help texts """

class HelpText(object):
    """
    text : str
        long version of help text
    brief : str
        short version of help text
    usage : str
        usage of the command
    
    This class contains the brief and long help textes for the commands
    """

    def __init__(self, text, brief, usage = ''):
        """ init for class. Sets long and brief help text and usage"""
        
        self.text = text
        self.brief = brief
        self.usage = usage


create_team_HelpText = HelpText(
    'Erstellt zwei zufällige Teams aus den Mitgliedern des Voice Channels und gegebenfalls weiteren, angegebene Spielern.',
    'Erstellt zwei zufällige Teams',
    '[names]'
)

move_team_HelpText = HelpText(
    'Bewegt die zwei mit !team create erstellten Teams in ihre entsprechenden Team Channel.',
    'Bewegt die zwei  Teams',
    ''
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

# TODO _join_ and _pass_ are different in every guild. How to solve that?
play_HelpText_long = 'und benachrichtigt alle User, die dieses Spiel auf dem Server aboniert haben. Auf die Anfrage kann mit ' + '_join_' + ' und ' + '_pass_' + ' reagiert werden, wodurch der Ersteller und bereits beigetretene Spieler eine Benachrichtigung erhalten.'

play_HelpText = HelpText(
    'Erstellt eine Spielanfrage ' + play_HelpText_long + ' Der Ersteller und die Spieler bekommen kurz vor Beginn des Spieles eine Nachricht.',
    'Erstellt eine Spielanfrage',
    'game (\'now\' | time)'
)

create_clash_HelpText = HelpText(
    'Erstellt eine Clash-Anfrage für das gegebene Datum ' + play_HelpText_long,
    'Erstellt eine Clash-Anfrage',
    'Datum'
)


player_HelpText = HelpText(
    'Gibt den Rang und die Winrate eines LoL-Spielers in EUW aus.',
    'Gibt Infos über LoL-Account aus.',
    'summonername'
)

smurf_HelpText = HelpText(
    'Überprüft, ob der angegebene Spieler wahrscheinlich ein Smurf ist.',
    'Überprüft ob ein Spieler ein Smurf ist.',
    'Spieler'
)

bans_HelpText = HelpText(
    'Bestimmt die besten Bans für ein 5er LoL-Team.',
    'Bestimmt Bans für LoL-Team.',
    'name1 name2 name3 name4 name5'
)

clash_HelpText = HelpText(
    'Liest aus einen Screenshot die Namen des Clashteams aus und gibt ihre op.gg-Links aus. Der Screenshot muss sich im Anhang befinden.',
    'Gibt den op.gg Namen des Clashteams aus.'
)