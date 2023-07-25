#!/usr/bin/python
# -*- coding: utf-8
import unittest,re
from cogs.prihlasky import Prihlasky

class TestStringMethods(unittest.TestCase):

    def test_jmeno(self):
        nick = Prihlasky.try_get_char(['Jméno postavy: test'])
        self.assertEqual('test', nick)

    def test_raiderio(self):
        nick = Prihlasky.try_get_char(['Link na armory (případně R.IO nebo warcraftlogs): https://raider.io/characters/eu/drakthul/raiderIO'])
        self.assertEqual('raiderIO', nick)

    def test_armory(self):
        nick = Prihlasky.try_get_char(['https://worldofwarcraft.com/en-gb/character/eu/drakthul/armory'])
        self.assertEqual('armory', nick)

    def test_armory_2(self):
        nick = Prihlasky.try_get_char(['https://worldofwarcraft.blizzard.com/en-gb/character/eu/drakthul/armory_2'])
        self.assertEqual('armory_2', nick)

    def test_bb(self):
        nick = Prihlasky.try_get_char(['https://worldofwarcraft.blizzard.com/en-gb/character/eu/burning-blade/burningblade'])
        self.assertEqual('burningblade', nick)

if __name__ == '__main__':
    unittest.main()

