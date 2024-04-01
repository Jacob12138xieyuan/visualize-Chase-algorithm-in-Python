"""
Author: Xie Yuan
Date: 2024-03-28

Copyright 2024 Xie Yuan
"""

import pandas as pd


class SimpleChaseChecker:
    def __init__(self):
        self.attributes = self.input_attributes()
        self.dependencies = self.input_dependencies()
        self.desired_dependency = self.input_chase_dependency()
        self.is_desired_dependency_mvd = "->>" in self.desired_dependency
        self.desired_x, self.desired_y = self.desired_dependency.split(
            "->>" if self.is_desired_dependency_mvd else "->")
        self.desired_xs = self.desired_x.split(",")
        self.desired_ys = self.desired_y.split(",")
        self.table = self.generate_initial_state()

    def generate_initial_state(self):
        data = []
        for i in range(2):
            row_values = [f"{attribute.lower() + str(i + 1)}" for attribute in self.attributes]
            data.append(row_values)
        # Create the initial DataFrame
        table = pd.DataFrame(data, columns=self.attributes)
        print("\nInitial Tuples:")
        print(table)
        return table

    def apply_dependency(self, d: str) -> bool:
        """
        Process each d as in current iteration.
        if d is functional dependency, find two tuple with same x, make y the same
        if d is multi-value dependency, copy the two rows with same x, swap their y values
        :param d:
        :return: modified table
        """
        # multi-value dependency
        if "->>" in d:
            # 'A->>B,C'
            x, y = d.split("->>")
            xs, ys = x.split(","), y.split(",")
            # find rows with same xs
            duplicated_rows = self.table[self.table.duplicated(subset=xs, keep=False)]
            if not len(duplicated_rows):
                return False
            # group by xs, swap each group two rows' ys
            groups = duplicated_rows.groupby(xs)
            for _, group_df in groups:
                group_df.reset_index(drop=True, inplace=True)
                # swap their ys values
                group_df.loc[0, ys], group_df.loc[1, ys] = group_df.loc[1, ys], group_df.loc[0, ys]
                # append two rows to df
                self.table = pd.concat([self.table, group_df], ignore_index=True)
        # functional dependency
        else:
            # 'D->C'
            x, y = d.split("->")
            xs, ys = x.split(","), y.split(",")
            # find rows with same xs
            duplicated_rows = self.table[self.table.duplicated(subset=xs, keep=False)]
            if not len(duplicated_rows):
                return False
            # group by xs, make their ys as the smaller subscript
            groups = duplicated_rows.groupby(xs)
            for _, group_df in groups:
                min_subscript_value = group_df[ys].min().item()  # Get the smallest 'C' value within the group
                # Update the ys column with the smallest value
                self.table.loc[group_df.index, ys] = min_subscript_value

        return True

    def run_simple_chase_algorithm(self) -> None:
        # make second row self.desired_x = first row
        print(f"\nDesired X is {self.desired_x}, make their value the same")
        self.table.loc[1, self.desired_xs] = self.table.loc[0, self.desired_xs]
        print(self.table)
        success = False
        # Start iterations
        for i, d in enumerate(self.dependencies):
            print(f"\nApplying the {i + 1} Dependency: {d}")
            result = self.apply_dependency(d)
            if not result:
                print("\nFunctional Dependency is violated")
                break

            print("\nTuples after Applying Functional Dependencies:")
            print(self.table)
            print(f"\nChecking if desired dependency {self.desired_dependency} fulfilled...")

            # check if desired dependency is fulfilled
            # case1: desired dependency is multi-value
            if self.is_desired_dependency_mvd:
                result = self.if_mvd_is_valid()
            # case2: desired dependency is functional
            else:
                # check if desired_ys are the same
                result = (self.table[self.desired_ys].nunique() == 1).item()

            # desired dependency fulfilled
            if result:
                success = True
                break

            # not last dependency, print continue
            if i != len(self.dependencies) - 1:
                print(
                    f"Desired dependency {self.desired_dependency} not fulfilled, continue applying other dependencies")
        if success:
            print(f"Congrats! Valid desired dependency {self.desired_dependency}!")
        else:
            print(f"Sorry! Invalid desired dependency {self.desired_dependency}.")

    def if_mvd_is_valid(self):
        # iterate each row pair, e.g. 1,2 1,3 1,4 2,3 2,4 ...
        # find the third tuple, tuple3.x == tuple1.x and tuple3.y == tuple1.y and tuple3.z == tuple2.z
        for i, row1 in enumerate(self.table.itertuples(index=False)):
            for j, row2 in enumerate(self.table.itertuples(index=False)):
                if j == i: continue
                # for each t1, t2, assume no third tuple exist
                exist = False
                for k, row3 in enumerate(self.table.itertuples(index=False)):
                    # the third tuple
                    row1_dict = row1._asdict()
                    row2_dict = row2._asdict()
                    row3_dict = row3._asdict()
                    # print(f"Currently row{i}, row{j}, checking if row{k} fulfill conditions")
                    union = set(self.desired_xs).union(self.desired_ys)
                    z = [z for z in self.attributes if z not in union]
                    if all(row3_dict[attr] == row1_dict[attr] for attr in self.desired_xs) and all(
                            row3_dict[attr] == row1_dict[attr] for attr in self.desired_ys) and all(
                            row3_dict[attr] == row2_dict[attr] for attr in z):
                        # print(
                        #     f"Found the third tuple row{k} {row3} with same {self.desired_x} and {self.desired_y} with row{i} {row1}, \n"
                        #     f"and the same {' and '.join(z)} with row{j} {row2}")
                        exist = True
                        break
                # after iterate all tuple other than row1, row2, not third tuple is found, means not fulfilled yet, continue next dependency
                if not exist:
                    print(f"For (row{i}, row{j}) pair, cannot find the third tuple to fulfill conditions")
                    return False
        return True

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
        # return ["A->>B", "B->>C"]

    @staticmethod
    def input_chase_dependency() -> str:
        chase_dependency_input = input("Enter desired dependency (e.g. A->C): ")
        return chase_dependency_input.strip()
        # return "A->>C"


# Calling the Chase algorithm with the input
# Positive example 1
# 4    A->>B,C;D->C      A->C
# Positive example 2
# 4    A->>B;B->>C       A->>C
# Negative example 3
# 4    A->>B,C;C,D->B    A->B
if __name__ == "__main__":
    checker = SimpleChaseChecker()
    checker.run_simple_chase_algorithm()
