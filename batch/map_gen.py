import hashlib
from random import Random
import sys
from pathlib import Path

N = 20
maps_dir = Path(sys.argv[1])
num_maps = 240


def generate(out_path: Path, seed: int):
    random = Random(seed)
    with out_path.open('w') as f:
        f.write(f'{N}\n')
        for _ in range(N):
            f.write(' '.join(str(random.randint(1, 1000)) for _ in range(N)))
            f.write('\n')


for i in range(num_maps):
    seed = hashlib.sha256(f"0zzv9dv {i}".encode()).digest()
    generate(maps_dir / str(i + 1), int.from_bytes(seed, 'big'))
