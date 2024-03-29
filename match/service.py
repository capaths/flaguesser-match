"""Match Service"""
import os
import random
import json
import unidecode

from hashlib import sha256

from nameko.rpc import rpc
from nameko.dependency_providers import Config

from match.models import MatchDatabase


def standardize_flag_name(name):
    return unidecode.unidecode(' '.join(name.lower().split(' ')))


class MatchService:
    name = "match"
    rep = MatchDatabase()
    config = Config()

    @staticmethod
    def get_flags(match_code: str, n_flags=20):
        path, _ = os.path.split(os.path.realpath(__file__))
        file = open(os.path.join(path, '../images.txt'), 'r')
        lines = file.readlines()
        file.close()

        random.seed(match_code)
        sample_list = random.sample(lines, n_flags)

        names, urls = list(), list()
        for line in sample_list:
            splitter = line.split(';')
            names.append(standardize_flag_name(splitter[2]))
            urls.append(splitter[3])

        return names, urls

    def get_flags_names(self, match_code: str, n_flags=20):
        return self.get_flags(match_code, n_flags)[0]

    @rpc
    def get_flags_images(self, match_code: str, n_flags=20):
        return self.get_flags(match_code, n_flags)[1]

    @rpc
    def guess_flag(self, match_code: str, country: str, n_flags=20):
        flag_names, flag_urls = self.get_flags(match_code, n_flags)
        s_country = standardize_flag_name(country)
        try:
            idx = flag_names.index(s_country)
            return flag_urls[idx]
        except ValueError:
            return None

    def match_to_dict(self, instance):
        dicto = dict()
        dicto['id'] = instance.id
        dicto['username1'] = instance.username1
        dicto['username2'] = instance.username2
        dicto['score1'] = instance.scoreP1
        dicto['score2'] = instance.scoreP2
        dicto['result'] = instance.result
        return dicto

    @rpc
    def get_all_matches(self):
        matches = self.rep.get_all_matches()
        array = []
        for instance in matches:
            array.append(self.match_to_dict(instance))
        return array

    @rpc
    def get_player_matches(self, username: str):
        matches = self.rep.get_player_matches(username)
        array = []
        for instance in matches:
            array.append(self.match_to_dict(instance))
        return array

    @rpc
    def generate_match_code(self, username1: str, username2: str, start_time: float):
        secret = self.config.get("SECRET", "secret")
        salt = f"match;{username1};{username2};{secret};{start_time}"
        code = sha256(salt.encode()).hexdigest()
        return code

    @rpc
    def end_match(self, username1, username2, score1, score2):
        if score1 > score2:
            result = 1
        elif score2 > score1:
            result = 2
        else:
            result = 0
        return self.rep.create_match(username1, username2, score1, score2, result)
