import time
import argparse
import threading
import utils
import json
import sys

def create_elements(args, collection):
    NUM_ITERATIONS = args.num_elements // args.num_threads

    def target(collection, operation):
        tid = threading.get_ident()
        for i in range(NUM_ITERATIONS):
            operation(tid, i, collection)

    threads = [threading.Thread(target=target, args=(collection, utils.add_operations[collection_type])) for _ in range(args.num_threads)]

    [thread.start() for thread in threads]
    [thread.join() for thread in threads]


def remove_elements(args, collection):
    assert args.num_elements % args.num_threads == 0, "Number of elements must be divisible by number of threads"

    NUM_ITERATIONS = args.num_elements // args.num_threads
    def target(collection, operation):
        for _ in range(NUM_ITERATIONS):
            operation(collection)

    threads = [threading.Thread(target=target, args=(collection, utils.remove_operations[collection_type])) for _ in range(args.num_threads)]
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]

def check_length(args, collection):
    def target(collection, iterations=args.num_iterations):
        for _ in range(iterations):
            len(collection)

    threads = [threading.Thread(target=target, args=(collection,)) for _ in range(args.num_threads)]

    [thread.start() for thread in threads]
    [thread.join() for thread in threads]

def move_elements(args, collections):
    assert args.num_elements % args.num_threads == 0, "Number of elements must be divisible by number of threads"
    _from, _to = collections

    NUM_ITERATIONS = args.num_elements // args.num_threads
    def target(_from, _to, operation):
        for _ in range(NUM_ITERATIONS):
            operation(_from, _to)

    threads = [threading.Thread(target=target, args=(_from, _to, utils.move_operations[collection_type])) for _ in range(args.num_threads)]
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]


def increment_elements(args, collection):
    assert type(collection) != set, "Cannot increment elements in a set"
    keys = list(range(args.num_elements))
    def target():
        for i in keys:
            collection[i] += 1
    threads = [threading.Thread(target=target) for _ in range(args.num_threads)]

    [thread.start() for thread in threads]
    [thread.join() for thread in threads]

def increment_integer(args, collection):
    integer = 0
    NUM_ITERATIONS = args.num_iterations // args.num_threads
    def target():
        nonlocal integer
        for _ in range(NUM_ITERATIONS):
            integer += 1

    threads = [threading.Thread(target=target) for _ in range(args.num_threads)]

    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    collection.append(integer)


commands = {
    "check_length": (check_length, lambda collection_type, args: utils.initialize_collection(collection_type, args.num_elements)),
    "remove_elements": (remove_elements, lambda collection_type, args: utils.initialize_collection(collection_type, args.num_elements)),
    "create_elements": (create_elements, lambda collection_type, args: utils.initialize_collection(collection_type, 0)),
    "increment_integer": (increment_integer, lambda collection_type, args: []),
    "move_elements": (
        move_elements,
        lambda collection_type, args: (
            utils.initialize_collection(collection_type, args.num_elements),
            utils.initialize_collection(collection_type, 0)
        )),
    "increment_elements": (increment_elements, lambda collection_type, args: utils.initialize_collection(collection_type, args.num_elements, set_zero=True))
}


def common_arguments(parser):
    parser.add_argument("--num_threads", type=int, default=1, help="Number of threads to use")
    parser.add_argument("--num_elements", type=int, default=1_000_000, help="Number of elements to remove")
    parser.add_argument("--num_iterations", type=int, default=1_000, help="Number of iterations each thread runs")
    parser.add_argument("--collection", type=str, choices=['list', 'set', 'dict'], default='list', help="Type of collection to use")


def add_subcommand(subparsers, name, help_text):
    parser_sub = subparsers.add_parser(name, help=help_text)
    common_arguments(parser_sub)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform operations concurrently on different collections.")
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    add_subcommand(subparsers, 'create_elements', 'Create elements in the collection')
    add_subcommand(subparsers, 'move_elements', 'Move elements between two collections')
    add_subcommand(subparsers, 'remove_elements', 'Remove elements from the collection')
    add_subcommand(subparsers, 'check_length', 'Check the length of the collection')
    add_subcommand(subparsers, 'increment_elements', 'Check the length of the collection')
    add_subcommand(subparsers, 'increment_integer', 'Increments a global integer')

    args = parser.parse_args()

    collection_type = utils.get_collection_type_from_name(args.collection)

    command_func, initialize_collection = commands[args.command]
    collection = initialize_collection(collection_type, args)

    # Begin command
    start = time.monotonic()
    command_func(args, collection)
    end = time.monotonic()
    results = {key: getattr(args, key) for key in vars(args)}
    results['time'] = end - start
    results['gil'] = int(sys._is_gil_enabled())
    print(sum(collection))
    print(json.dumps(results))
