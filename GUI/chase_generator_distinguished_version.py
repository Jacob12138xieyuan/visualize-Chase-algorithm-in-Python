"""
Author: Xie Yuan
Date: 2024-04-01

Copyright 2024 Xie Yuan
"""

import pandas as pd
import re
from common import return_df_pretty


class DistinguishedVariableChaseChecker:
    def __init__(self, input_option, input_attributes, input_dependencies, input_desired_decompositions_dependency):
        self.option = input_option
        self.attributes = input_attributes

        dependencies_list = input_dependencies.split(";")
        dependencies = [dependency.strip() for dependency in dependencies_list]
        self.dependencies = dependencies
        # check lossless
        if self.option == 1:
            decompositions_input = input_desired_decompositions_dependency
            decomposition_matches = re.findall(r'(\w+)\((.*?)\)', decompositions_input)
            decompositions = []
            for match in decomposition_matches:
                values = [v.strip() for v in match[1].split(",")]
                decompositions.append(values)
            self.desired_decompositions = decompositions
        # check dependency
        else:
            self.desired_dependency = input_desired_decompositions_dependency.strip()
            self.is_desired_dependency_mvd = "->>" in self.desired_dependency
            self.desired_x, self.desired_y = self.desired_dependency.split(
                "->>" if self.is_desired_dependency_mvd else "->")
            self.desired_xs = self.desired_x.split(",")
            self.desired_ys = self.desired_y.split(",")
        self.table = self.generate_initial_state()

    def generate_initial_state(self) -> pd.DataFrame:
        """
        Generate initial state table
        :return:
        """
        data = []
        for i in range(len(self.desired_decompositions) if self.option == 1 else 2):
            row_values = [f"{attribute.lower() + str(i + 1)}" for attribute in self.attributes]
            data.append(row_values)
        # Create the initial DataFrame
        table = pd.DataFrame(data, columns=self.attributes)
        # print("\nInitial Tuples:")
        # print_df_pretty(table)
        return table

    def change_initial_tuple(self):
        """
        Preprocess state table according to 3 cases
        :return:
        """
        str = ''
        if self.option == 1:
            # for each decomposition, e.g. 1st A,B,D, make 1st row all columns alpha
            aa = f"\nFor columns in each decomposition, distinguish their values in corresponding tuple."
            for i, decomposition in enumerate(self.desired_decompositions):
                self.table.loc[i, decomposition] = 'α'
            str = aa
        else:
            if self.is_desired_dependency_mvd:
                # For each A ∈ X ∪ Y , distinguish A−values in the first tuple.
                union = list(set(self.desired_xs).union(self.desired_ys))
                bb = f"\nFor columns in {union}, distinguish their values in the first tuple."
                self.table.loc[0, union] = 'α'
                # For each A ∈ X ∪ (R − X − Y ), Distinguish A−values in the second tuple.
                other_columns = list(set(self.desired_xs).union(set(self.attributes).difference(set(self.desired_xs)).difference(set(self.desired_ys))))
                cc = f"For columns in {other_columns}, distinguish their values in the second tuple."
                self.table.loc[1, other_columns] = 'α'
                str = bb + '\n' + cc
            else:
                # Distinguish the values of the first tuple.
                dd = "\nDistinguish the values of the first tuple."
                self.table.loc[0] = 'α'
                # For each A ∈ X, distinguish the A−values in the second tuple.
                ee = f"For columns in {self.desired_xs}, distinguish their values in the second tuple."
                self.table.loc[1, self.desired_xs] = 'α'
                str = dd + '\n' + ee
        return ('\n' + str + '\n',return_df_pretty(self.table))

    def chase_generator(self) -> None:
        """
        Main chase algorithm
        :return:
        """
        result = self.change_initial_tuple()
        yield result
        success = False
        # Start iterations
        # note: we should consider the sequence of dependencies
        while self.dependencies:
            d = self.dependencies.pop(0)
            aa = f"\nTry to apply the dependency: {d}"
            yield aa
            # print(f"\nTry to apply the dependency: {d}")
            result = self.apply_dependency(d)
            # if cannot apply this dependency
            if not result:
                # it is the last dependency, we fail
                if not self.dependencies:
                    bb = "Cannot apply this dependency. And it is the last dependency, dependency is violated"
                    yield bb
                    # print("Cannot apply this dependency. And it is the last dependency, dependency is violated")
                # it is not the last dependency, we apply other first
                else:
                    cc = "Cannot apply this dependency. It is not the last dependency, apply the next dependency first"
                    yield cc
                    # print("Cannot apply this dependency. It is not the last dependency, apply the next dependency first")
                    # append it to the end for later use
                    self.dependencies.append(d)
                    continue
            # successfully applied this dependency
            dd = "Tuples after Applying Dependency:"
            yield dd
            # print("Tuples after Applying Dependency:")
            tt = return_df_pretty(self.table)
            yield tt

            if self.option == 1:
                ee = f"\nChecking if one tuple has all same value α..."
                yield ee
                # print(f"\nChecking if one tuple has all same value α...")
                # Chase until you find a row of distinguished variables.
                result = self.if_found_one_tuple_with_same_value()
                if result:
                    ff = f"Found a row of distinguished variables."
                    yield ff
                    # print(f"Found a row of distinguished variables.")
            else:
                if self.is_desired_dependency_mvd:
                    ff = f"\nChecking if can find a row of distinguished variables..."
                    yield ff
                    # print(f"\nChecking if can find a row of distinguished variables...")
                    # Chase until you find a row of distinguished variables.
                    result = self.if_found_one_tuple_with_same_value()
                    if result:
                        gg = f"Found a row of distinguished variables."
                        yield gg
                        # print(f"Found a row of distinguished variables.")
                else:
                    hh = f"\nChecking if can find the Y−columns {self.desired_ys} of distinguished variables..."
                    yield hh
                    # print(f"\nChecking if can find the Y−columns {self.desired_ys} of distinguished variables...")
                    # Chase until you find the Y−columns of distinguished variables.
                    result = self.if_found_y_columns_with_same_value()
                    if result:
                        ii = f"Found the Y−columns {self.desired_ys} of distinguished variables."
                        yield ii
                        # print(f"Found the Y−columns {self.desired_ys} of distinguished variables.")

            if result:
                success = True
                break

            # if still have dependencies
            if self.dependencies:
                if self.option == 1:
                    jj = f"Cannot find a row of distinguished variables, continue applying other dependencies"
                    yield jj
                else:
                    if self.is_desired_dependency_mvd:
                        kk = f"Cannot find a row of distinguished variables, continue applying other dependencies"
                        yield kk
                        # print(
                        #     f"Cannot find a row of distinguished variables, continue applying other dependencies")
                    else:
                        ll = f"Cannot find the Y−columns {self.desired_ys} of distinguished variables."
                        yield ll
                        # print(f"Cannot find the Y−columns {self.desired_ys} of distinguished variables.")

        if success:
            if self.option == 1:
                mm = f"\nCongrats! The desired decomposition {self.desired_decompositions} is lossless!"
                yield mm
                # print(f"\nCongrats! The desired decomposition {self.desired_decompositions} is lossless!")
            else:
                nn = f"\nCongrats! Valid desired dependency {self.desired_dependency}!"
                yield nn
                # print(f"\nCongrats! Valid desired dependency {self.desired_dependency}!")
        else:
            if self.option == 1:
                oo = f"\nSorry! The desired decomposition {self.desired_decompositions} is not lossless."
                yield oo
                # print(f"\nSorry! The desired decomposition {self.desired_decompositions} is not lossless.")
            else:
                pp = f"\nSorry! Invalid desired dependency {self.desired_dependency}."
                yield pp
                # print(f"\nSorry! Invalid desired dependency {self.desired_dependency}.")

    def apply_dependency(self, d: str) -> bool:
        """
        Process each d as in current iteration.
        if d is functional dependency, find tuples with same x, make y the same
        if d is multi-value dependency, copy the two rows pairs with same x, swap their y values
        :param d: each dependency
        :return: if successful
        """
        # multi-value dependency
        if "->>" in d:
            x, y = d.split("->>")
            xs, ys = x.split(","), y.split(",")
            # find rows with same xs
            duplicated_rows = self.table[self.table.duplicated(subset=xs, keep=False)]
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
                        self.table = pd.concat([self.table, pair], ignore_index=True)
        # functional dependency
        else:
            x, y = d.split("->")
            xs, ys = x.split(","), y.split(",")
            # find rows with same xs
            duplicated_rows = self.table[self.table.duplicated(subset=xs, keep=False)]
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
                    self.table.loc[group_df.index, ys] = 'α'
                else:
                    min_subscript_value = group_df[ys].min().item()
                    # Update the ys column with the smallest value
                    self.table.loc[group_df.index, ys] = min_subscript_value
        return True

    def if_found_one_tuple_with_same_value(self):
        return self.table.apply(lambda row: all(value == 'α' for value in row), axis=1).any()

    def if_found_y_columns_with_same_value(self):
        return (self.table[self.desired_ys] == 'α').all().all()

    @staticmethod
    def input_option() -> int:
        option = int(input("Do you want to chase dependency (0) or lossless decomposition (1): "))
        assert option in [0, 1]
        print(f"You selected chasing {'lossless decomposition' if option == 1 else 'dependency'}")
        return option

    @staticmethod
    def input_attributes() -> list:
        num_attributes = int(input("Enter number of attributes (e.g. 4): "))
        attributes = [chr(ord('A') + i) for i in range(num_attributes)]
        print("Attributes list: {}".format(', '.join(attributes)))
        return attributes

    @staticmethod
    def input_dependencies() -> list[str]:
        dependencies_input = input("Enter functional/multi-value dependencies separated by ';' (e.g. A->>B,C;D->C): ")
        dependencies_list = dependencies_input.split(";")
        dependencies = [dependency.strip() for dependency in dependencies_list]
        return dependencies

    @staticmethod
    def input_desired_dependency() -> str:
        chase_dependency_input = input("Enter desired dependency (e.g. A->C): ")
        return chase_dependency_input.strip()

    @staticmethod
    def input_desired_decompositions():
        decompositions_input = input(
            "Enter desired decompositions separated by ';' (e.g. R1(A,B,D);R2(A,C)): ")
        decomposition_matches = re.findall(r'(\w+)\((.*?)\)', decompositions_input)
        decompositions = []
        for match in decomposition_matches:
            values = [v.strip() for v in match[1].split(",")]
            decompositions.append(values)
        return decompositions


# Calling the Chase algorithm with the example input

# option 0: check lossless
# Positive example 1
# 3    C->B                        R1(A,C);R2(B,C)
# Positive example 2
# 6    B->E;E,F->C;B,C->A;A,D->E   R1(A,B,C,F);R2(A,D,E);R3(B,D,F)
# Negative example 3
# 3    A->C                        R1(A,B);R2(B,C)
# Positive example 4
# 4    A->>B;B->>C                 R1(A,B);R2(B,C);R3(A,D)
# Positive example 5
# 4    A->>B;B->>C                 R1(A,B,D);R2(A,C)

# option 1: check new dependency
# positive example 1
# 4    A->>B,C;D->C      A->C
# positive example 2
# 4    A->>B;B->>C       A->>C
# negative example 3
# 4    A->>B,C;C,D->B    A->B
if __name__ == "__main__":
    checker = DistinguishedVariableChaseChecker()
    checker.run_chase_algorithm()