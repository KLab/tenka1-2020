import sys
from pathlib import Path
import redis
from time import time
import os

maps_dir = Path(sys.argv[1])
num_maps = int(sys.argv[2])
if sys.argv[3][0] == '+':
    start_at0 = int(time() * 1000) + int(sys.argv[3])
else:
    start_at0 = int(sys.argv[3])
game_length = int(sys.argv[4])

gamedb_host = os.environ.get('GAMEDB_HOST', 'localhost')
gamedb_port = int(os.environ.get('GAMEDB_PORT', '6379'))

red = redis.Redis(host=gamedb_host, port=gamedb_port, db=0)

red.delete('map_info')
red.delete('start_at')
red.delete('end_at')
red.delete('ranking_game_id')
red.delete('ranking_coef')

start_at = {}
end_at = {}
for i in range(num_maps):
    game_id = str(i + 1)
    with (maps_dir / game_id).open() as f:
        red.hset('map_info', game_id, f.read().rstrip('\n'))
    start_at[game_id] = start_at0 + i * game_length
    end_at[game_id] = start_at0 + (i + 1) * game_length
    red.hset('ranking_coef', game_id, 10 ** (i // 60))

red.hmset('start_at', start_at)
red.zadd('end_at', end_at)
