import unittest
from aepeash_final import *


class TestRank(unittest.TestCase):
    def test_bar_search(self):
        results = process_command('rank')
        self.assertEqual(results[0][0], 1)

        results = process_command('rank bottom')
        self.assertEqual(results[0][0], 115)

class TestPlayerPoints(unittest.TestCase):
    def test_bar_search(self):
        results = process_command('player_points')
        self.assertEqual(results[0][0], 'Casey Harkins')

        results = process_command('player_points bottom')
        self.assertEqual(results[0][0], 'Michaela Bruno')


class TestTeamPoints(unittest.TestCase):
    def test_bar_search(self):
        results = process_command('team_points')
        self.assertEqual(results[0][0], 34)

        results = process_command('team_points bottom')
        self.assertEqual(results[0][0], 39)


class TestPlayerSaves(unittest.TestCase):
    def test_bar_search(self):
        results = process_command('player_saves')
        self.assertEqual(results[0][0], 'Alex Salim')

        results = process_command('player_saves bottom')
        self.assertEqual(results[0][0], 'Sarah Zeto')


class TestTeamSaves(unittest.TestCase):
    def test_bar_search(self):
        results = process_command('team_saves')
        self.assertEqual(results[0][0], 74)

        results = process_command('team_saves bottom')
        self.assertEqual(results[0][0], 29)


if __name__ == '__main__':

    unittest.main()

