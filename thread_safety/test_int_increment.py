import threading

value = 0

def increment(num_iter):
    global value
    for _ in range(num_iter):
        value += 1

NUM_THREADS = 100
NUM_ELEMENTS = 1_000_000
NUM_ITERS = NUM_ELEMENTS // NUM_THREADS
assert NUM_ELEMENTS % NUM_THREADS == 0, "Invalid number of elements"

threads = [threading.Thread(target=increment, args=(NUM_ITERS,)) for _ in range(NUM_THREADS)]

[value_thread.start() for value_thread in threads]
[value_thread.join() for value_thread in threads]
print(value)
