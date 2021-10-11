# coding=utf-8


def mapMerge(mappingA, mappingB):
    """
    Merge two dictionaries such that the result is a superset of both, or {} if there
    is a conflict

    Example:
    mapMerge({}, {B:P|Q}) -> {B:P|Q}
    mapMerge({A:P&Q}, {B:P|Q}) -> {A:P&Q, B:P|Q}
    mapMerge({A:P, B:P|Q}, {B:P|Q}) -> {A:P, B:P|Q}
    mapMerge({A:P, B:P|Q}, {A:P&Q, B:P|Q}) -> {}

    @param mappingA - A dict to merge
    @param mappingB - A dict to merge
    @return - A dict that is the smallest superset of mappingA and mappingB, or None
    is there is a conflict
    """

    # Base case either map is empty, trivially return the other
    if not mappingA or len(mappingA) == 0:
        return mappingB
    if not mappingB or len(mappingB) == 0:
        return mappingA

    from copy import copy

    # Make merge a copy of mappingA
    merge = copy(mappingA)

    # For each entry in mappingB
    for b in mappingB:
        # If it is already in the merge and their values are not equal then no merge
        # exists
        if b in merge and mappingB[b] != merge[b]:
            if mappingB[b] <= merge[b]:
                pass
            elif merge[b] <= mappingB[b]:
                continue
            else:
                return {}
        # Otherwise add it to the merge
        merge[b] = mappingB[b]

    return merge
