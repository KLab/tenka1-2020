import os
import subprocess
import sys
from urllib.request import urlopen

GAME_SERVER = os.getenv('GAME_SERVER', 'https://contest.gbc-2020.tenka1.klab.jp')
TOKEN = os.getenv('TOKEN', 'YOUR_TOKEN')


p = subprocess.Popen(sys.argv[1:], stdin=subprocess.PIPE, stdout=subprocess.PIPE)


def call_api(x: str):
    with urlopen(f'{GAME_SERVER}{x}') as res:
        p.stdin.write(res.read())
        p.stdin.flush()


while True:
    line = p.stdout.readline()
    if not line:
        break
    a = line.decode().rstrip().split(' ')
    if a[0] == 'game':
        call_api('/api/game')
    elif a[0] == 'stage':
        call_api(f'/api/stage/{a[1]}')
    elif a[0] == 'claim':
        call_api(f'/api/claim/{TOKEN}/{a[1]}/{a[2]}')
    elif a[0] == 'areas':
        call_api(f'/api/areas/{TOKEN}/{a[1]}')
    elif a[0] == 'ranking':
        call_api(f'/api/ranking/{TOKEN}/{a[1]}')
    else:
        assert False, f'invalid command {repr(a[0])}'
