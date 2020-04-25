import unittest

from aepeash_final import *

class TestRank(unittest.TestCase):
    def test_bar_search(self):
        results = process_command('rank')
        self.assertEqual(results[0][2], '43')

        results = process_command('rank bottom')
        self.assertEqual(results[0][0], '115')

class TestPlayerPoints(unittest.TestCase):
    def test_bar_search(self):
        results = process_command('player_points')
        self.assertEqual(results[0][0], '1')

        results = process_command('player_points')
        self.assertEqual(results[0][0], '115')


class TestTeamPoints(unittest.TestCase):
    def test_bar_search(self):
        results = process_command('team_points')
        self.assertEqual(results[0][0], '1')

        results = process_command('team_points bottom')
        self.assertEqual(results[0][0], '115')


class TestPlayerSaves(unittest.TestCase):
    def test_bar_search(self):
        results = process_command('player_saves')
        self.assertEqual(results[0][0], '1')

        results = process_command('player_saves bottom')
        self.assertEqual(results[0][0], '115')


class TestTeamSaves(unittest.TestCase):
    def test_bar_search(self):
        results = process_command('team_saves')
        self.assertEqual(results[0][0], '1')

        results = process_command('team_saves bottom')
        self.assertEqual(results[0][0], '115')



unittest.main()

