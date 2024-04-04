"""
# Time       :2024/4/3 20:49
# Author     :Li Yijia, Xie Yuan
"""

import pandas as pd
from common import print_df_pretty
from itertools import combinations


def generate_initial_state(attributes):
    """
    Generate initial state table
    :return:
    """
    data = []
    for i in range(2):
        row_values = [f"{attribute.lower() + str(i + 1)}" for attribute in attributes]
        data.append(row_values)
    # Create the initial DataFrame
    table = pd.DataFrame(data, columns=attributes)
    print("\nInitial Tuples:")
    print_df_pretty(table)
    return table


def apply_dependency(d, table) -> bool:
    """
    Process each d as in current iteration.
    if d is functional dependency, find tuples with same x, make y the same
    if d is multi-value dependency, copy the two rows pairs with same x, swap their y values
    :param d: each dependency
    :param table: table
    :return: if successful
    """
    # multi-value dependency
    if "->>" in d:
        x, y = d.split("->>")
        xs, ys = x.split(","), y.split(",")
        # find rows with same xs
        duplicated_rows = table[table.duplicated(subset=xs, keep=False)]
        if not len(duplicated_rows):
            return False
        # group by xs, each group may have more than two rows, swap each pair two rows' ys
        groups = duplicated_rows.groupby(xs)
        for _, group_df in groups:
            group_df.reset_index(drop=True, inplace=True)

            for i in range(len(group_df)):
                for j in range(i + 1, len(group_df)):
                    pair = group_df.iloc[[i, j]]
                    pair.reset_index(drop=True, inplace=True)
                    # swap their ys values
                    pair.loc[0, ys], pair.loc[1, ys] = pair.loc[1, ys], pair.loc[0, ys]
                    table = pd.concat([table, pair], ignore_index=True)
    # functional dependency
    else:
        x, y = d.split("->")
        xs, ys = x.split(","), y.split(",")
        # find rows with same xs
        duplicated_rows = table[table.duplicated(subset=xs, keep=False)]
        if not len(duplicated_rows):
            return False
        # group by xs,
        # if one row's ys is alpha, make other ys alpha
        # else if one row has small subscript
        groups = duplicated_rows.groupby(xs)
        for _, group_df in groups:
            alpha_exists = 'α' in group_df[ys].values
            # Update the ys column with 'α'
            if alpha_exists:
                table.loc[group_df.index, ys] = 'α'
            else:
                min_subscript_value = group_df[ys].min().item()
                # Update the ys column with the smallest value
                table.loc[group_df.index, ys] = min_subscript_value
    return True


def if_found_one_tuple_with_same_value(table):
    return table.apply(lambda row: all(value == 'α' for value in row), axis=1).any()


def if_found_y_columns_with_same_value(table, desired_ys):
    return (table[desired_ys] == 'α').all().all()


def change_initial_tuple(table, dependency, desired_xs, desired_ys, attributes):
    """
    Preprocess state table according to 3 cases
    :return:
    """
    if is_mvd(dependency):
        # For each A ∈ X ∪ Y , distinguish A−values in the first tuple.
        union = list(set(desired_xs).union(desired_ys))
        print(f"\nFor columns in {union}, distinguish their values in the first tuple.")
        table.loc[0, union] = 'α'
        # For each A ∈ X ∪ (R − X − Y ), Distinguish A−values in the second tuple.
        other_columns = list(set(desired_xs).union(
            set(attributes).difference(set(desired_xs)).difference(set(desired_ys))))
        print(f"For columns in {other_columns}, distinguish their values in the second tuple.")
        table.loc[1, other_columns] = 'α'
    else:
        # Distinguish the values of the first tuple.
        print("\nDistinguish the values of the first tuple.")
        table.loc[0] = 'α'
        # For each A ∈ X, distinguish the A−values in the second tuple.
        print(f"For columns in {desired_xs}, distinguish their values in the second tuple.")
        table.loc[1, desired_xs] = 'α'
    print_df_pretty(table)


def run_chase_algorithm(relation, covers, attributes) -> bool:
    """
    Main chase algorithm
    :return:
    """
    # Start iterations
    # note: we should consider the sequence of dependencies

    # delete one cover a time, if this cover is entailed by the left covers, then the whole one is not minimal cover
    sigma = convert_to_sigma(relation)
    for cover in covers:
        table = generate_initial_state(attributes=attributes)
        desired_xys = findxy(cover)
        desired_xs = desired_xys[0].split(",")
        desired_ys = desired_xys[1].split(",")
        if len(desired_ys) > 1:
            print("\nSorry! Your cover is not a none-compact minimal cover because of more than one attribute in the right hand side!")
            return False
        closure_this_cover = find_closure(desired_xs, sigma)
        all_subsets = find_subsets(desired_xs)
        for each_subset_attribute in all_subsets:
            closure_temp = find_closure(each_subset_attribute, sigma)
            if closure_temp == closure_this_cover:
                return False
        change_initial_tuple(table, cover, desired_xs, desired_ys, attributes)
        cover_pop_fd = covers_without_fd(covers, cover)
        for fd in cover_pop_fd:
            result = apply_dependency(fd, table)
            # successfully applied this dependency
            if result:
                print("\nTuples after Applying Dependency:")
                print_df_pretty(table)
            else:
                print("\nNothing changed using this dependency")
            if if_found_y_columns_with_same_value(table, desired_ys):
                print("\nSorry! Your cover is not a minimal cover!")
                return False

    for fd in relation:
        table = generate_initial_state(attributes)

        desired_xys = findxy(fd)
        desired_xs = desired_xys[0].split(",")
        desired_ys = desired_xys[1].split(",")

        change_initial_tuple(table, fd, desired_xs, desired_ys, attributes)

        # start chase
        for cover in covers:
            result = apply_dependency(cover, table)
            # successfully applied this dependency
            if result:
                print("\nTuples after Applying Dependency:")
                print_df_pretty(table)
            else:
                print("\nNothing changed using this dependency")
        if not if_found_y_columns_with_same_value(table, desired_ys):
            print("\nSorry! Your cover is not a minimal cover!")
            return False
    print("\nCongrats! Your cover is a minimal cover!")
    return True


def covers_without_fd(covers, cover):
    return [c for c in covers if c != cover]


def is_mvd(fd):
    return "->>" in fd

def convert_to_sigma(fd_list):
    sigma = []
    for fd in fd_list:
        left, right = fd.split("->")
        left_attrs = set(left.split(","))
        right_attrs = set(right.split(","))
        sigma.append((left_attrs, right_attrs))
    return sigma


def findxy(fd):
    desired_x, desired_y = fd.split(
        "->>" if is_mvd(fd) else "->")

    return (desired_x, desired_y)


def input_attributes() -> list:
    num_attributes = int(input("Enter number of attributes (e.g. 4): "))
    attributes = [chr(ord('A') + i) for i in range(num_attributes)]
    print("Attributes list: {}".format(', '.join(attributes)))
    return attributes

def find_subsets(S):
    subsets = []
    for r in range(1, len(S)):
        subsets.extend(combinations(S, r))
    return subsets

def find_closure(S, sigma):

    unused = sigma.copy()  # Ω stands for 'unused'
    closure = set(S)  # Γ stands for 'closure'

    while any(X <= closure for X, Y in unused):
        X, Y = next((X, Y) for X, Y in unused if X <= closure)
        unused.remove((X, Y))
        closure.update(Y)

    return closure
def input_dependencies() -> list[str]:
    dependencies_input = input("Enter functional dependencies separated by ';' (e.g. A->B;B->C)")
    dependencies_list = dependencies_input.split(";")
    dependencies = [dependency.strip() for dependency in dependencies_list]
    return dependencies

def input_covers() -> list[str]:
    dependencies_input = input(
        "Enter functional cover you want to test separated by ';' (e.g. A->B;B->C) \n(Notice you cannot have more than one attribute in the right hand side， otherwise it is not a non-compact minimal cover): ")
    dependencies_list = dependencies_input.split(";")
    dependencies = [dependency.strip() for dependency in dependencies_list]
    return dependencies
# covers1 = ['B->D','B->E','A,F->B','F->C']
# covers2 = ['B->D','D,F->C','D->E','A,F->B']
# relations = ['B->D','D,F->C','B,D->E','A,F->B','A,D,F->B,C']

if __name__ == "__main__":
    attributes = input_attributes()
    relations = input_dependencies()
    covers = input_covers()
    run_chase_algorithm(relations, covers, attributes)

