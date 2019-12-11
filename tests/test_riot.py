import sys
import os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'modules'))
import unittest
import riot


    # populate_with_debug_data()
    # assert(len(players) == 2)
    # removePlayer("Thya")
    # assert(len(players) == 1)
    # assert(get_champion_id_by_name("Pyke") == 555)
    # assert(get_champion_name_by_id(555) == "Pyke")
    # assert(list(get_most_played_champs(0, 2)) == ['Pyke', 'Blitzcrank'])
    # assert(format_last_time_played(get_last_time_played_by_id(0, 555)) == "20-11-2019")
    # assert(format_last_time_played(get_last_time_played_by_name(0, "Pyke")) == "20-11-2019")
    # assert(has_played_champ_by_name_in_last_n_days(0, "Pyke",30) == True)
    # winrate, rank = get_soloq_data(0)
    # assert(winrate == 52.8)
    # assert(rank == 'DIAMOND-IV')
    # assert(get_soloq_rank_weight(rank) == 7)
    # assert(isSmurf(0) == False)
    # assert(get_level(0)== 119)
    # assert(get_best_ban(0) == ['Pyke', 'Blitzcrank', 'Caitlyn', 'Zoe', 'Kaisa'])
    # populate_with_debug_data()
    # assert(get_best_bans_for_team() == ['Pyke'])


class TestRiot(unittest.TestCase):
    def test_get_champion_id_by_name(self):
        self.assertEqual(riot.get_champion_id_by_name("Pyke"), 555)

    def test_get_champion_name_by_id(self):
        self.assertEqual(riot.get_champion_name_by_id(555), "Pyke")

if __name__ == '__main__':
    unittest.main()