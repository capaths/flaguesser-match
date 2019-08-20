"""Match Service"""

import json, random
from nameko.web.handlers import http
from nameko.rpc import rpc
from match.models import Match, MatchDatabase
from match.schemas import MatchSchema
from nameko.exceptions import BadRequest

import os


class MatchService:
    name = "match"
    rep = MatchDatabase()

    @rpc
    def create_match(self, username1, username2, score1, score2):
        if score1 > score2:
            result = 1
        elif score2 > score1:
            result = 2
        else:
            result = 0

        return self.rep.create_match(username1, username2, score1, score2, result)

    @http('POST', '/match')
    def post_match(self, request):
        schema = MatchSchema(strict=True)
        try:
            match_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        username1 = match_data['username1']
        username2 = match_data['username2']
        score1 = match_data['scorePlayer1']
        score2 = match_data['scorePlayer2']

        if self.create_match(username1, username2, score1, score2):
            return 200, ""
        return 500, ""

    @rpc
    def get_flags(self, n_flags=20):
        path, _ = os.path.split(os.path.realpath(__file__))
        file1 = open(os.path.join(path, '../images.txt'), 'r')
        sample_list = random.sample(range(0, 70), n_flags)

        name, url = [], []
        for i in file1:
            splitter = i.split(';')
            if int(splitter[0]) in sample_list:
                name.append(splitter[2])
                url.append(splitter[3])

        data = [{"name": t, "image_url": s} for t, s in zip(name, url)]
        return data

    @rpc
    def get_all_matches(self):
        matches = self.rep.get_all_matches()
        array = []
        for instance in matches:
            dicto = dict()
            dicto['id'] = instance.id
            dicto['username1'] = instance.username1
            dicto['username2'] = instance.username2
            dicto['score1'] = instance.scoreP1
            dicto['score2'] = instance.scoreP2
            dicto['result'] = instance.result
            array.append(dicto)
        return array

    @rpc
    def get_player_matches(self, username):
        matches = self.rep.get_player_matches(username)
        return matches
