import re
from tabulate import tabulate


def check_if_str_has_subscript(string):
    matches = re.match(r"([a-zA-Z]+)(\d*)", string)
    digit_part1 = matches.group(2)
    return True if digit_part1 else False


def apply_functional_dependencies(table: dict[str, dict], fd: list):
    """
    Process each fd as an iteration. Find two tuple with same x, make y the same
    :param table: e.g.
    {'R1(A, C)': {'A': 'a', 'B': 'b1', 'C': 'c'},
     'R2(B, C)': {'A': 'a2', 'B': 'b', 'C': 'c'}}
    :param fd:
    :return: modified table
    """
    x_attributes, y_attribute = fd
    rows_with_same_attributes = None
    seen_attribute_values = {}

    for key, row in table.items():
        attribute_values = tuple(row.get(attr) for attr in x_attributes)
        if attribute_values in seen_attribute_values:
            matching_key = seen_attribute_values[attribute_values]
            matching_row = table[matching_key]
            rows_with_same_attributes = (matching_key, matching_row, key, row)
            break
        else:
            seen_attribute_values[attribute_values] = key

    # no two rows with same x_attributes value
    if not rows_with_same_attributes:
        return None

    # print the two rows with same attributes
    matching_key, matching_row, key, row = rows_with_same_attributes
    print(f"Matching rows with same attributes '{x_attributes}':")
    # print(f"Row 1: {matching_key}, Row 1 values: {matching_row}")
    # print(f"Row 2: {key}, Row 2 values: {row}")

    y_value1 = table[matching_key][y_attribute]
    y_value2 = table[key][y_attribute]

    # if y_value1 and y_value2 both have subscript, make second value same as first value
    # if one y_attribute value has not subscript, make two value no subscript
    has_subscript1 = check_if_str_has_subscript(y_value1)
    has_subscript2 = check_if_str_has_subscript(y_value2)

    # y_value1 and y_value2 both have subscript
    updated_row_key = None
    if has_subscript1 and has_subscript2:
        table[key][y_attribute] = y_value1
    # y_value1 has subscript and y_value2 has no subscript
    elif has_subscript1 and not has_subscript2:
        table[matching_key][y_attribute] = y_value2
        updated_row_key = matching_key
    # y_value1 has no subscript and y_value2 has subscript
    elif not has_subscript1 and has_subscript2:
        table[key][y_attribute] = y_value1
        updated_row_key = key

    return (table, updated_row_key)


def print_dict_as_table(dictionary):
    """
    Print tuple table pretty
    +-----------------+-----+-----+-----+
    | Decomposition   | A   | B   | C   |
    +=================+=====+=====+=====+
    | R1(A, C)        | a   | b1  | c   |
    +-----------------+-----+-----+-----+
    | R2(B, C)        | a2  | b   | c   |
    +-----------------+-----+-----+-----+
    :param dictionary:
    :return:
    """
    if not dictionary:
        print("Dictionary is empty.")
        return

    keys = list(dictionary.keys())
    values = list(dictionary.values())
    headers = ['Decomposition'] + sorted(values[0].keys())

    table = []
    for key, value in zip(keys, values):
        row = [key] + [value[attr] for attr in sorted(value.keys())]
        table.append(row)

    print(tabulate(table, headers, tablefmt="grid"))


def chase_algorithm(attributes, functional_dependencies, decompositions):

    # Generate initial table
    table = {key: {} for key in decompositions}
    for attr in attributes:
        for index, key in enumerate(table.keys()):
            table[key][attr] = attr.lower() if attr in decompositions[key] else attr.lower() + str(index + 1)

    print("Initial Tuples:")
    print_dict_as_table(table)

    for i, fd in enumerate(functional_dependencies):
        print("\nApplying the {} Functional Dependencies: {} -> {}".format(i+1, fd[0], fd[1]))
        result = apply_functional_dependencies(table, fd)

        if not result:
            print("\nFunctional Dependency is violated, lossy decomposition!!!")
            break

        new_table, updated_row_key = result

        print("\nTuples after Applying Functional Dependencies:")
        print_dict_as_table(new_table)

        # check if updated row has no subscript at all
        if updated_row_key:
            no_subscript = True
            updated_row = new_table[updated_row_key]  # {'A': 'a', 'B': 'b', 'C': 'c'}
            for value in updated_row.values():
                if check_if_str_has_subscript(value):
                    no_subscript = False
                    break
            if no_subscript:
                print("\nCongrats! No violation found in decompositions! Decomposition is lossless!!!")
                break


def main():
    # Taking input from the user
    num_attributes = int(input("Enter the number of attributes (e.g. 6): "))
    attributes = [chr(ord('A') + i) for i in range(num_attributes)]
    print("Attributes list: {}".format(', '.join(attributes)))

    functional_dependencies_input = input("Enter the functional dependencies separated by ',' (e.g. B->E,EF->C,BC->A,AD->E): ")
    functional_dependencies_list = functional_dependencies_input.split(",")
    functional_dependencies = []
    for fd in functional_dependencies_list:
        fd = fd.split("->")
        fd = [f.strip() for f in fd]
        functional_dependencies.append(fd)

    decompositions_input = input("Enter the desired decompositions separated by ',' (e.g. R1(A,B,C,F),R2(A,D,E)R3(B,D,F)): ")
    decomposition_matches = re.findall(r'(\w+)\((.*?)\)', decompositions_input)
    decompositions = {}
    for match in decomposition_matches:
        key = match[0].strip() + "(" + match[1].strip() + ")"
        values = [v.strip() for v in match[1].split(",")]
        decompositions[key] = values

    # execute chase algorithm
    chase_algorithm(attributes, functional_dependencies, decompositions)


if __name__ == "__main__":
    # Calling the Chase algorithm with the input
    # Positive example 1
    # 3    C->B                     R1(A,C), R2(B,C)
    # Positive example 2
    # 6    B->E,EF->C,BC->A,AD->E   R1(A,B,C,F),R2(A,D,E),R3(B,D,F)
    # Negative example 3
    # 3    A->C                     R1(A,B),R2(B,C)
    main()
