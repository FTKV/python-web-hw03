import concurrent.futures
from multiprocessing import Pool, cpu_count
import logging
from random import randint
from time import time


CPU_COUNT = cpu_count()


logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def get_divisors(number):
    divisors = [1]
    for i in range(2, int(number / 2) + 1):
        if number % i == 0:
            divisors.append(i)
    divisors.append(number)
    return divisors


def get_divisors_of_numbers_single_process(*numbers):
    timer = time()
    result = []
    for number in numbers:
        divisors = get_divisors(number)
        result.append(divisors)
    logging.debug(f"Done with single process in {time() - timer} seconds\n")
    return tuple(result)


def get_divisors_of_numbers_multi_process_v1(*numbers):
    timer = time()
    with Pool(processes=CPU_COUNT) as pool:
        result = pool.map(get_divisors, numbers)
    logging.debug(f"Done with {CPU_COUNT} multi processes (Pool from multiprocessing) in {time() - timer} seconds\n")
    return tuple(result)


def get_divisors_of_numbers_multi_process_v2(*numbers):    
    timer = time()
    with concurrent.futures.ProcessPoolExecutor(CPU_COUNT) as executor:
        result = executor.map(get_divisors, numbers)
    logging.debug(f"Done with {CPU_COUNT} multi processes (ProcessPoolExecutor from concurrent.futures) in {time() - timer} seconds\n")
    return tuple(result)


if __name__ == "__main__":

    N = 10**3
    MIN, MAX = 10**6, 10**7

    numbers = []
    for i in range(N):
        numbers.append(randint(MIN, MAX))

    logging.debug(f"\nFinding all divisors for {N} random integers in range from {MIN} to {MAX-1}:\n")

    result1 = get_divisors_of_numbers_single_process(*numbers)
    result2 = get_divisors_of_numbers_multi_process_v1(*numbers)
    result3 = get_divisors_of_numbers_multi_process_v2(*numbers)

    logging.debug(f"Equivalence of all results: {result1 == result2 == result3}")
