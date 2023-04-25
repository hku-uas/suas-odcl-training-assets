import time
from typing import Optional

from tqdm import tqdm

from src.utils.func_static_vars import static_vars


@static_vars(last=time.perf_counter())
def stopwatch(section_name: Optional[str] = None):
    now = time.perf_counter()
    elapsed = now - stopwatch.last
    if section_name is not None:
        tqdm.write(f"[Stopwatch][{section_name}]: {elapsed:.4f}s")
    stopwatch.last = time.perf_counter()
