import uuid

def get_collection_type_from_name(name):
    return {
        'list': list,
        'set': set,
        'dict': dict
    }[name]

def initialize_collection(collection_type, num_elements, set_zero=False):
    if collection_type == list:
        return [0 if set_zero else i for i in range(num_elements)]
    elif collection_type == set:
        return {0 if set_zero else i for i in range(num_elements)}
    elif collection_type == dict:
        return {i: 0 if set_zero else 1 for i in range(num_elements)}
    else:
        raise ValueError("Unsupported collection type")


remove_operations = {
    list: lambda c: c.pop(),
    set: lambda c: c.pop(),
    dict: lambda c: c.popitem(),
}

# tid: thread id
# i: iteration
# c: collection
add_operations = {
    list: lambda tid, i, c: c.append(i),
    set: lambda tid, i, c: c.add((tid, i)),
    dict: lambda tid, i, c: c.setdefault((tid, i), 1),
}

move_operations = {
    list: lambda from_, to: to.append(from_.pop()),
    set: lambda from_, to: to.add(from_.pop()),
    dict: lambda from_, to: to.update({from_.popitem()}),
}
