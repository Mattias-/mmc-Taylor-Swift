
import sys
import time
import json
import requests

import ai

#GAME_URL = 'http://competition.monkeymusicchallenge.com/game'
GAME_URL = 'http://54.171.110.188/game'

if len(sys.argv) < 4:
    print('Usage: python index.py <your-team-name> <your-api-key> <game-id>\n')
    if len(sys.argv) < 1:
        print('  Missing argument: <your-team-name>')
    if len(sys.argv) < 2:
        print('  Missing argument: <your-api-key>')
    if len(sys.argv) < 3:
        print('  Missing argument: <game-id>')
    sys.exit(1)

TEAM_NAME = sys.argv[1]
API_KEY = sys.argv[2]
GAME_ID = sys.argv[3]

def post_to_server(command):
    command['team'] = TEAM_NAME
    command['apiKey'] = API_KEY
    command['gameId'] = GAME_ID

    reply = requests.post(GAME_URL,
                          data=json.dumps(command),
                          headers={'Content-Type': 'application/json'})

    if reply.status_code != requests.codes.ok:
        print('  The server replied with status code %d' % reply.status_code)
        try:
            print('  %s' % reply.json()['message'])
        except:
            pass
        sys.exit(1)
    current_game_state = reply.json()
    return current_game_state

current_game_state = post_to_server({'command': 'join game'})

monkey = ai.Monkey(current_game_state)
while not current_game_state['isGameOver']:
    print('Remaining turns: %d' % current_game_state['remainingTurns'])
    start = time.time()
    monkey.set_state(current_game_state)
    next_command = monkey.get_command()
    current_game_state = post_to_server(next_command)
    print 'Time: %f' % (time.time() - start)

print "My points: %d, Enemy points: %d to %d" % (monkey.score,
                                                 monkey.enemy_est_score(),
                                                 monkey.enemy_max_score())
print('\nDone!\n')
