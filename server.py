from flask_restful import Resource, Api, reqparse
from flask import Flask, Response
import urllib3
import copy


urllib3.disable_warnings()

app = Flask(__name__)
api = Api(app)

start_game = {
    'users': {
        '1': {
            'name': '',
            'role': ''
        },
        '2': {
            'name': '',
            'role': ''
        }
    },
    'game_field': [
        ['', '', ''],
        ['', '', ''],
        ['', '', '']
    ],
    'who_win': None,
    'who_turn': None
}
patterns_to_win = [
    [[0, 0], [0, 1], [0, 2]],
    [[1, 0], [1, 1], [1, 2]],
    [[2, 0], [2, 1], [2, 2]],

    [[0, 0], [1, 0], [2, 0]],
    [[0, 1], [1, 1], [2, 1]],
    [[0, 2], [1, 2], [2, 2]],

    [[0, 0], [1, 1], [2, 2]],
    [[0, 2], [1, 1], [2, 0]],
]

games = {
    '1': {
        'users': {
            '1': {
                'name': 'Vanya',
                'role': 'x'
            },
            '2': {
                'name': 'Dima',
                'role': 'o'
            }
        },
        'game_field': [
            ['x', 'o', ''],
            ['',  'x', ''],
            ['',  '',  'o']
        ],
        'who_win': None,
        'who_turn': 'Vanya'
    }
}


def get_all_pos(field, role):
    res = []
    for i in range(len(field)):
        for j in range(len(field[i])):
            if field[i][j] == role:
                res.append([i, j])

    return res


def check_win(game_id):
    game = games[game_id]
    field = game['game_field']

    user_1 = game['users']['1']
    user_2 = game['users']['2']

    user_1_pos = get_all_pos(field, user_1['role'])
    user_2_pos = get_all_pos(field, user_2['role'])

    for i in patterns_to_win:
        count = 0
        for j in user_1_pos:
            for k in i:
                if k == j:
                    count += 1
        if count == len(i):
            game['who_win'] = user_1['name']
            break

        count = 0
        for j in user_2_pos:
            for k in i:
                if k == j:
                    count += 1

        if count == len(i):
            game['who_win'] = user_2['name']
            break


class GetGame(Resource):
    def __init__(self):
        req = reqparse.RequestParser()
        req.add_argument('game_id', type=str, required=True)
        req.add_argument('user_name', type=str, required=True)

        args = req.parse_args()
        self.game_id = args['game_id']
        self.user_name = args['user_name']

    def get(self):
        r = Response()
        if not games.get(self.game_id) or not (games[self.game_id]['users']['1']['name'] == self.user_name or
                                               games[self.game_id]['users']['2']['name'] == self.user_name):
            r.status_code = 404
        else:
            return games[self.game_id]

        return r


class EnjoyGame(Resource):
    def __init__(self):
        req = reqparse.RequestParser()
        req.add_argument('game_id', type=str, required=True)
        req.add_argument('user_name', type=str, required=True)
        req.add_argument('role', type=str, default='x')

        args = req.parse_args()
        self.game_id = args['game_id']
        self.user_name = args['user_name']
        self.role = args['role']

    def post(self):
        r = Response()
        if not self.game_id or not self.user_name or self.role not in ('x', 'o'):
            r.status_code = 416
        elif games.get(self.game_id):
            if games[self.game_id]['users']['1']['name'] == self.user_name or \
                    games[self.game_id]['users']['2']['name'] == self.user_name:
                return games[self.game_id]

            if games[self.game_id]['users']['2']['name'] == '':
                games[self.game_id]['users']['2']['name'] = self.user_name
                if not games[self.game_id]['who_turn']:
                    games[self.game_id]['who_turn'] = self.user_name

                return games[self.game_id]

            r.status_code = 416
        else:
            new_game = copy.deepcopy(start_game)
            games[self.game_id] = new_game

            new_game['users']['1']['name'] = self.user_name
            new_game['users']['1']['role'] = self.role
            new_game['users']['2']['role'] = 'x' if self.role == 'o' else 'o'
            new_game['who_turn'] = self.user_name

            return new_game

        return r


class StepGame(Resource):
    def __init__(self):
        req = reqparse.RequestParser()
        req.add_argument('game_id', type=str, required=True)
        req.add_argument('user_name', type=str, required=True)
        req.add_argument('x', type=int, required=True)
        req.add_argument('y', type=int, required=True)

        args = req.parse_args()
        self.game_id = args['game_id']
        self.user_name = args['user_name']
        self.x = args['x']
        self.y = args['y']

    def post(self):
        r = Response()
        if not games.get(self.game_id):
            r.status_code = 404
        elif not self.game_id or not self.user_name or not (0 <= self.x <= 2) \
                or not (0 <= self.y <= 2) or games[self.game_id].get('who_win') or \
                games[self.game_id]['who_turn'] != self.user_name:
            r.status_code = 416
        else:
            users = games[self.game_id]['users']
            role = None
            for user in users.values():
                if user['name'] == self.user_name:
                    role = user['role']
                    break

            if role:
                field = games[self.game_id]['game_field']

                if not field[self.y][self.x]:
                    for i in users.values():
                        if self.user_name != i['name']:
                            games[self.game_id]['who_turn'] = i['name']
                            break

                    field[self.y][self.x] = role
                    check_win(self.game_id)

                return games[self.game_id]

            r.status_code = 406

        return r


class GetAllGames(Resource):
    def get(self):
        return games


api.add_resource(GetGame, '/get_game')
api.add_resource(EnjoyGame, '/enjoy_game')
api.add_resource(StepGame, '/step_game')
api.add_resource(GetAllGames, '/get_all_games')


if __name__ == '__main__':
    app.run('0.0.0.0', port=6000, debug=True)
