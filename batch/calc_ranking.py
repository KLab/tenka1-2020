import json
import sys
from pathlib import Path
import redis
from time import time, sleep
import subprocess
import os

N = 20 * 20
PERIOD = 2000
DELAY_TIME = 1500
calc_score_path = Path(sys.argv[1]).resolve()
maps_dir = Path(sys.argv[2])

gamedb_host = os.environ.get('GAMEDB_HOST', 'localhost')
gamedb_port = int(os.environ.get('GAMEDB_PORT', '6379'))
gamedb_pass = os.environ.get('GAMEDB_PASSWORD')

calc_time = int(time() * 1000) // PERIOD * PERIOD
while calc_time - int(time() * 1000) <= PERIOD - DELAY_TIME:
    calc_time += PERIOD
ranking_time = calc_time - PERIOD

sleep_time = (calc_time - (PERIOD - DELAY_TIME)) / 1000 - time()
sleep(sleep_time)

start_time = time()  # todo

red = redis.Redis(host=gamedb_host, port=gamedb_port, db=0, password=gamedb_pass)

game_id = red.get('ranking_game_id')
game_id = 1 if game_id is None else int(game_id)
end_at = red.zscore('end_at', game_id)
if end_at is None:
    sys.exit(0)
# print(f'game_id = {game_id}')
# print(f'end_at = {end_at}')

claim = {}

tmp_file = Path('tmp_file')
if tmp_file.exists():
    with tmp_file.open() as f:
        x = json.loads(f.read())
        if x['game_id'] == game_id:
            claim = x['claim']

user_ids = [x.decode() for x in red.hkeys(f'claim_unlock_{game_id}')]

min_claim_time = red.getset(f'min_claim_time_{game_id}', ranking_time)
min_claim_time = int(min_claim_time) if min_claim_time else 0
print(f'min_claim_time {repr(min_claim_time)}')

for user_id in user_ids:
    a = set()
    if user_id in claim:
        a = set(claim[user_id])
    a |= {int(e) for e in red.zrangebyscore(f'claim_{game_id}_{user_id}', min_claim_time, ranking_time)}
    claim[user_id] = list(a)

num_claim = [0 for _ in range(N)]
for a in claim.values():
    for e in a:
        num_claim[e] += 1

with tmp_file.open('w') as f:
    f.write(json.dumps({'game_id': game_id, 'claim': claim, 'ranking_time': ranking_time}))

red_time = time()  # todo

calc_score_args = [str(calc_score_path), str(maps_dir / str(game_id))]
p = subprocess.Popen(calc_score_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
ranking_data = {}
for user_id, cl in claim.items():
    input_str = f'{len(cl)}\n' + ''.join(f'{e} {num_claim[e]}\n' for e in cl)
    p.stdin.write(input_str.encode())
    p.stdin.flush()
    line = p.stdout.readline()
    ranking_data[user_id] = float(line)
p.stdin.close()

end_time = time()  # todo
print('recv:  ', red_time - start_time)
print('calc:  ', end_time - red_time)
print('total: ', end_time - start_time)

sleep_time = calc_time / 1000 - time()
if sleep_time > 0:
    sleep(sleep_time)

# print(ranking_data)
if ranking_data:
    red.zadd(f'ranking_{game_id}', ranking_data)

if end_at <= ranking_time:
    print('ranking_game_id', game_id + 1)
    red.set('ranking_game_id', game_id + 1)
    ranking_total = {k.decode(): v for k, v in red.zrange('ranking_total', 0, -1, withscores=True)}
    coef = float(red.hget('ranking_coef', game_id))
    for user_id, score in ranking_data.items():
        if user_id in ranking_total:
            ranking_total[user_id] += score * coef
        else:
            ranking_total[user_id] = score * coef
    if ranking_total:
        red.zadd('ranking_total', ranking_total)
