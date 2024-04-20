from itertools import combinations
from collections import OrderedDict


def get_all_attributes(fds: list[list]) -> list:
    """
    Generate all attributes from 'A'
    """
    # method 1: sequence
    # max_char = ''
    # for fd in fds:
    #     lhs, rhs = fd
    #     for char in ''.join(lhs + rhs):
    #         if char > max_char:
    #             max_char = char
    # # found max_char. e.g. F
    # return [chr(char_code) for char_code in range(ord('A'), ord(max_char) + 1)]

    # method 2: attributes in fds
    attributes_set = set()
    for fd in fds:
        lhs, rhs = fd
        attributes_set.update(set(lhs))
        attributes_set.update(set(rhs))
    return list(sorted(attributes_set))

    # method 3:
    # return ['A','B','C','D','E','G','H']


def cal_attribute_closure(attributes: set, fds: list[list]):
    """
    It is a fix point algorithm
    attribute: set of attribute like {'A', 'E'}
    fds: a list of fd
    """
    closure = attributes.copy()
    changed = True
    while changed:
        changed = False
        for lhs, rhs in fds:
            if set(lhs).issubset(closure) and not set(rhs).issubset(closure):
                # union
                closure.update(rhs)
                changed = True
    return closure


def cal_combination_attribute_closure(all_attributes, fds: list[list], continue_same_length=True, continue_longer_length=False):
    """
    Generate combinations of attributes until superkey is found
    """
    # all_attributes = get_all_attributes(fds)
    combs = OrderedDict()
    superkeys = []
    for i in range(len(all_attributes) - 1):
        found_superkey = False
        for comb in combinations(all_attributes, i + 1):
            # comb is tuple type, comb contain any superkey is a superkey
            if any(set(superkey).issubset(comb) for superkey in superkeys):
                continue
            attribute_closure = cal_attribute_closure(set(comb), fds)
            combs[tuple(sorted(comb))] = attribute_closure
            # check if comb is superkey
            if attribute_closure == set(all_attributes):
                superkeys.append(comb)
                found_superkey = True
                # continue same length attributes check
                if not continue_same_length:
                    break
        # continue other length attributes check
        if found_superkey and not continue_longer_length: break
    return superkeys, combs


def is_redundant(fd, fds):
    """
    Check if fd can be derived from other fds
    :param fd: the fd we need to check
    :param fds: other fds except fd
    :return: bool
    """
    remaining_fds = fds.copy()
    # remove fd from fds first
    remaining_fds.remove(fd)
    X, Y = fd
    closure = cal_attribute_closure(set(X), remaining_fds)
    # after apply other fds, whether we find X->Y, which is Y in closure of X
    return set(Y).issubset(closure)


def remove_duplicate_fds(fds):
    """
    Remove duplicate fds in fds and maintain the order
    :param fds: a list of functional dependencies
    :return: new list of functional dependencies without duplicate
    """
    seen = set()
    new_fds = []
    for fd in fds:
        str_item = str(fd)  # Convert inner lists to strings for set comparison
        if str_item not in seen:
            seen.add(str_item)
            new_fds.append(fd)
    return new_fds


def get_compact_min_cover(fds):
    compact_fds_dict = {}
    compact_fds = []
    for fd in fds:
        lhs, rhs = fd
        lhs = tuple(lhs)
        if lhs not in compact_fds_dict:
            compact_fds_dict[lhs] = rhs
        else:
            compact_fds_dict[lhs] += rhs
    for lhs, rhs in compact_fds_dict.items():
        compact_fds.append([list(lhs), rhs])
    return compact_fds


def min_cover(all_attributes, fds):
    print(f"Original dependencies: \n{fds}")

    # Step 1: Decompose the right-hand side (RHS) of each dependency
    fds1 = []
    for fd in fds:
        lhs, rhs = fd
        for rhs_attribute in rhs:
            fds1.append([lhs, [rhs_attribute]])
    print(f"After minimize RHS: \n{fds1}")

    # Step 2: Minimize the left-hand side (LHS) of each dependency
    # Calculate attribute closure
    _, attribute_closures = cal_combination_attribute_closure(all_attributes, fds1)
    fds2 = []
    for fd in fds1:
        lhs, rhs = fd
        # remove trivial dependency, e.g. A,B->A
        if set(rhs).issubset(set(lhs)):
            continue
        # lhs is already minimized
        if len(lhs) == 1:
            fds2.append(fd)
        # lhs is not minimized
        else:
            # find first attribute closure which contains rhs
            for attributes_set, closure in attribute_closures.items():
                # e.g. 'F' should not be in attributes_set, this is trivial
                if set(rhs).issubset(closure) and (not set(rhs).issubset(attributes_set)):
                    fds2.append([sorted(list(attributes_set)), rhs])
                    break
    # remove duplicate fd
    fds2 = remove_duplicate_fds(fds2)
    print(f"After minimize LHS: \n{fds2}")

    # Step 3: Check if each fd is redundant. i.e. fd can be derived from other fds
    # if you want to find the last solution, uncomment below
    fds2 = fds2[::-1]
    # find the first solution
    min_cover = []
    remaining_fds2 = fds2.copy()
    for fd in fds2:
        if is_redundant(fd, remaining_fds2):
            remaining_fds2.remove(fd)
        else:
            min_cover.append(fd)
    # if you want to find the last solution, uncomment below
    min_cover = min_cover[::-1]
    print(f"After remove redundant: \n{min_cover}")
    return min_cover


def generate_all_min_covers(fds: list[list]) -> list[list]:
    """
    To minimize fds itself (remove redundant in all possible ways)
    :param fds:
    :return:
    """
    all_min_covers = []

    def backtrack(cur_min_cover, remaining_fds, index):
        if index == len(remaining_fds):
            # remaining fds cannot contain redundant
            no_redundant_fd = True
            for fd in remaining_fds:
                if is_redundant(fd, remaining_fds):
                    no_redundant_fd = False
                    break
            if no_redundant_fd: all_min_covers.append(cur_min_cover)
            return

        cur_fd = remaining_fds[index]
        if is_redundant(cur_fd, remaining_fds):
            # don't select cur_min_cover
            backtrack(cur_min_cover, remaining_fds[:index] + remaining_fds[index + 1:], index)
        # select cur_min_cover
        backtrack(cur_min_cover + [cur_fd], remaining_fds, index + 1)

    backtrack([], fds, 0)
    return all_min_covers


def min_covers(fds):
    print(f"Original dependencies: \n{fds}")

    # Step 1: Decompose the right-hand side (RHS) of each dependency
    fds1 = []
    for fd in fds:
        lhs, rhs = fd
        for rhs_attribute in rhs:
            fds1.append([lhs, [rhs_attribute]])
    print(f"After minimize RHS: \n{fds1}")

    # Step 2: Minimize the left-hand side (LHS) of each dependency
    # Calculate attribute closure
    _, attribute_closures = cal_combination_attribute_closure(fds1)
    fds2 = []
    for fd in fds1:
        lhs, rhs = fd
        # remove trivial dependency, e.g. A,B->A
        if set(rhs).issubset(set(lhs)):
            continue
        # lhs is already minimized
        if len(lhs) == 1:
            fds2.append(fd)
        # lhs is not minimized
        else:
            # find first attribute closure which contains rhs
            for attributes_set, closure in attribute_closures.items():
                # e.g. 'F' should not be in attributes_set, this is trivial
                if set(rhs).issubset(closure) and (not set(rhs).issubset(attributes_set)):
                    fds2.append([sorted(list(attributes_set)), rhs])
                    break
    # remove duplicate fd
    fds2 = remove_duplicate_fds(fds2)
    print(f"After minimize LHS: \n{fds2}")

    # Step 3: Check if fd is redundant. i.e. can be derived from other fds
    min_covers = generate_all_min_covers(fds2)
    print(f"After remove redundant, multiple possible min_covers: \n{min_covers}")
    return min_covers


def generate_all_reachable_pairs(fds):
    """
    Use dfs to get each node's all reachable node
    :param fds:
    :return:
    """
    graph = {}
    reachable_pairs = []

    # Build the graph
    for fd in fds:
        X, Y = fd
        if X[0] not in graph:
            graph[X[0]] = set()
        graph[X[0]].add(Y[0])

    # Perform DFS
    def dfs(visited, start_node, current_node):
        visited.add(start_node)
        for neighbor in graph.get(current_node, []):
            if neighbor not in visited:
                reachable_pairs.append([[start_node], [neighbor]])
                dfs(visited, start_node, neighbor)

    for node in graph.keys():
        # generate pairs where A can reach
        visited = set()
        dfs(visited, node, node)

    return reachable_pairs


def all_min_covers(fds):
    # graph dfs, start from A, can reach B,C; start from B, can reach A,C; start from C, can reach A,B
    # we have [[['A'],['B']], [['A'],['C']], [['B'],['C']], [['B'],['A']], [['C'],['A']], [['C'],['B']]]
    # generate its min covers
    fds1 = generate_all_reachable_pairs(fds)
    all_min_covers = min_covers(fds1)
    return all_min_covers


def is_fds_in_BCNF(fds, superkeys):
    """
    Input is minimal cover (compact minimal cover also can)
    Condition: trivial or lhs is superkey
    :param fds:
    :return: bool
    """
    print(f"\nChecking R with fds {fds} is in BCNF...")
    in_BCNF = True
    first_violate_fd = None
    for fd in fds:
        lhs, rhs = fd
        if tuple(lhs) in superkeys:
            print(f"Checking {fd}, lhs is a superkey! It is in BCNF.")
        else:
            in_BCNF = False
            if not first_violate_fd: first_violate_fd = fd
            print(f"Checking {fd}, lhs is not a superkey! Is is not in BCNF.")
    print(f"Relation R with fds is {'' if in_BCNF else 'not '}in BCNF.")
    return in_BCNF, first_violate_fd


def is_fds_in_3NF(fds, superkeys):
    """
    Input is minimal cover (compact minimal cover also can)
    Condition: trivial or lhs is superkey or all attribute in rhs is prime attribute
    :param fds:
    :return: bool
    """
    print(f"\nChecking R with fds {fds} is in 3NF...")
    prime_attributes = set()
    for superkey in superkeys:
        prime_attributes.update(superkey)
    print(f"Prime attributes: {prime_attributes}")
    in_3NF = True
    for fd in fds:
        lhs, rhs = fd
        if tuple(lhs) in superkeys:
            print(f"Checking {fd}, lhs is a superkey, it is in 3NF.")
        elif all(element in prime_attributes for element in rhs):
            print(f"Checking {fd}, rhs are prime attributes, it is in 3NF.")
        else:
            in_3NF = False
            print(f"Checking {fd}, it is not in 3NF.")
    print(f"Relation R with fds is {'' if in_3NF else 'not '}in 3NF.")
    return in_3NF


def is_fds_in_2NF(fds, superkeys):
    """
    Input is minimal cover (compact minimal cover also can)
    Condition: trivial or all attribute in rhs is prime attribute or lhs is not proper subset of any candidate key
    :param fds:
    :return: bool
    """
    print(f"\nChecking R with fds {fds} is in 2NF...")
    prime_attributes = set()
    for superkey in superkeys:
        prime_attributes.update(superkey)
    print(f"Prime attributes: {prime_attributes}")
    in_2NF = True
    for fd in fds:
        lhs, rhs = fd
        if all(element in prime_attributes for element in rhs):
            print(f"Checking {fd}, rhs are prime attributes, it is in 2NF.")
        elif not any(set(lhs).issubset(set(superkey)) and set(lhs) != set(superkey) for superkey in superkeys):
            print(f"Checking {fd}, lhs is not proper subset of any candidate key, it is in 2NF.")
        else:
            in_2NF = False
            print(f"Checking {fd}, it is not in 2NF.")
    print(f"Relation R with fds is {'' if in_2NF else 'not '}in 2NF.")
    return in_2NF


def decompose_to_3NF_synthesis_algo(fds):
    """
    Decompose to 3NF. If compact minimal cover has 3 fds, we decompose it into three relations
    lossless and dependency preserving
    :return:
    """
    print("\nSynthesis decompose algo")
    n = len(fds)
    Rs = []
    Fs = []
    for i in range(n):
        lhs, rhs = fds[i]
        attributes = list(sorted(set(lhs).union(set(rhs))))
        Rs.append(attributes)
        F = []
        for fd in fds:
            lhs, rhs = fd
            if set(lhs).issubset(set(attributes)):
                intersection = set(rhs).intersection(set(attributes))
                if intersection:
                    F.append([lhs, list(intersection)])
        Fs.append(F)
        print(f"R{i+1}: {attributes} with F{i+1}: {F}")

    def is_redundant(R, remaining_Rs):
        redundant = False
        for R_ in remaining_Rs:
            if R != R_ and set(R).issubset(set(R_)):
                redundant = True
                break
        return redundant

    # remove redundant R and F
    print("Remove redundant R and F")
    final_Rs = []
    final_Fs = []
    remaining_Rs = Rs.copy()
    remaining_Fs = Fs.copy()
    for i, R in enumerate(Rs):
        F = Fs[i]
        if is_redundant(R, remaining_Rs):
            remaining_Rs.remove(R)
            remaining_Fs.remove(F)
        else:
            final_Rs.append(R)
            final_Fs.append(F)

    for i, R in enumerate(final_Rs):
        F = final_Rs[i]
        print(f"R{i+1}: {R} with F{i+1}: {F}")


def decompose_to_BCNF_recursive(R, F):
    superkeys, combs = cal_combination_attribute_closure(R, F)
    in_BCNF, violate_fd = is_fds_in_BCNF(F, superkeys)
    if in_BCNF:
        return [R], [F]
    Rs = []
    Fs = []
    print(f"\nDecomposing R {R} on violated fd {violate_fd}")
    attributes = R
    lhs, rhs = violate_fd
    R1 = sorted((set(attributes) - set(combs[tuple(lhs)])).union(set(lhs)))
    R2 = sorted(set(combs[tuple(lhs)]))
    F1 = []
    F2 = []
    for fd in F:
        lhs, rhs = fd
        if set(lhs).issubset(set(R1)):
            intersection = set(rhs).intersection(set(R1))
            if intersection: F1.append([lhs, list(intersection)])
        if set(lhs).issubset(set(R2)):
            intersection = set(rhs).intersection(set(R2))
            if intersection: F2.append([lhs, list(intersection)])
    print(f"Decompose to BCNF R1: {R1} with F1: {F1}, R2: {R2} with F2 {F2}")
    R1_, F1_ = decompose_to_BCNF_recursive(R1, F1)
    R2_, F2_ = decompose_to_BCNF_recursive(R2, F2)
    Rs += R1_
    Rs += R2_
    Fs += F1_
    Fs += F2_
    return Rs, Fs


fds = [[['A','B'], ['B','C']], [['C'], ['A','C']], [['B','C','D'],['A','B','D','E']], [['C','D'],['D','E']], [['E'],['D','E']], [['A','B','E'],['C','D','E']]]
# fds = [[['A','B'], ['C']], [['C'], ['A']]]

# fds = [[['A','B'], ['C','D','E']], [['A','C'], ['B','D','E']], [['B'],['C']], [['C'],['B']], [['C'],['D']], [['B'],['E']], [['C'],['E']]]
# fds = [[['B'], ['C']], [['C'], ['B','D','E']]]
# fds = [[['A'], ['B','C','D','E']], [['D'], ['E']]]
# fds = [[['A','B','C'], ['B','D','E']], [['A','B','C'], ['A','C','G','H']], [['B'],['B','D','E']], [['G'],['B','D','E']]]
# fds = [[['A', 'B'], ['C']], [['C'], ['B']]]
all_attributes = get_all_attributes(fds)
superkeys, combs = cal_combination_attribute_closure(all_attributes, fds)
print("Superkeys: ", superkeys)
print("Closures: ", combs)
min_cov = min_cover(all_attributes, fds)
print("Min cover: ", min_cov)
compact_min_cov = get_compact_min_cover(min_cov)
print("Compact min cover: ", compact_min_cov)

Rs, Fs = decompose_to_BCNF_recursive(all_attributes, compact_min_cov)
print(f"\nRelation {all_attributes} with F {compact_min_cov} can be decomposed to: ")
if len(Rs) > 1:
    for i, R in enumerate(Rs):
        print(f"R{i+1}: {R}, F{i+1}: {Fs[i]}")

in_3NF = is_fds_in_3NF(compact_min_cov, superkeys)
if not in_3NF:
    decompose_to_3NF_synthesis_algo(compact_min_cov)

in_2NF = is_fds_in_2NF(compact_min_cov, superkeys)

