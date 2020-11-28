import requests
import config
from time import sleep


def input_mod(message):
    string = ''
    while not string:
        string = input(message)
        if not string:
            print('Input is empty, please, try again')

    return string


class Server:
    @staticmethod
    def get_game(game_id, user_name):
        res = requests.get(f'{config.server}/get_game', params={'game_id': game_id, 'user_name': user_name})
        if res.status_code == 200:
            return res.json()

    @staticmethod
    def enjoy_game(game_id, user_name):
        res = requests.post(f'{config.server}/enjoy_game', params={'game_id': game_id, 'user_name': user_name})
        if res.status_code == 200:
            return res.json()

    @staticmethod
    def step_game(game_id, user_name, x, y):
        res = requests.post(f'{config.server}/step_game', params={'game_id': game_id, 'user_name': user_name,
                                                                  'x': x, 'y': y})
        if res.status_code == 200:
            return res.json()


class Client:
    def __init__(self):
        self.name = None
        self.game_id = None
        self.game = None

    def view(self):
        if self.game:
            user_1 = self.game['users']['1']
            user_2 = self.game['users']['2']
            print('User 1: {} role: ({}) | User 2: {} role: ({})'.format(user_1['name'], user_1['role'],
                                                                         user_2['name'], user_2['role']))

            for i in self.game['game_field']:
                for j in i:
                    if j == '':
                        print(' ', end=' ')
                    else:
                        print(j, end=' ')
                print()

            if not self.game['who_win']:
                print('Now turn is {}'.format(self.game['who_turn']))

            if self.game['who_win']:
                print('{} WON!'.format(self.game['who_win']))

    def enjoy_game(self):
        game = Server.enjoy_game(self.game_id, self.name)
        if game:
            self.game = game

    def get_game(self):
        game = Server.get_game(self.game_id, self.name)
        if game:
            self.game = game

    def step_game(self, x, y):
        game = Server.step_game(self.game_id, self.name, x, y)
        if game:
            self.game = game

    def main(self):
        self.name = input_mod('Enter a name: ')
        print(f'Hi {self.name}!')

        self.game_id = input_mod('Enter a game id: ')
        self.enjoy_game()

        if not self.game:
            print('Name or Game id do not valid')
            return

        print(f'You successful enjoy to {self.game_id}')

        run = True
        old_game = None
        while run:
            if old_game != self.game:
                self.view()
                old_game = self.game

            if self.game['who_turn'] == self.name and not self.game['who_win']:
                x = input_mod('Enter x: ')
                y = input_mod('Enter y: ')

                self.step_game(x, y)

            sleep(0.2)
            self.get_game()


if __name__ == '__main__':
    client = Client()
    client.main()
