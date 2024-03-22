from tkinter import *
import re
from tkinter import messagebox
from typing import Any
from tabulate import tabulate


class LosslessDecompositionChecker:
    def __init__(self, num, fd, de):
        # Taking input from the user
        # attributes = ['A', 'B', 'C', 'D', 'E', 'F']
        # functional_dependencies = [['B', 'E'], ['EF', 'C'], ['BC', 'A'], ['AD', 'E']]
        # decompositions = {'R1(A,B,C,F)': ['A', 'B', 'C', 'F'], 'R2(A,D,E)': ['A', 'D', 'E'], 'R3(B,D,F)': ['B', 'D', 'F']}
        self.attributes = self.input_attributes(num)
        self.functional_dependencies = self.input_functional_dependencies(fd)
        self.decompositions = self.input_decompositions(de)
        self.table = self.generate_initial_state()
        # self.print_table()

    def generate_initial_state(self):
        table = {key: {} for key in self.decompositions}
        for attr in self.attributes:
            for index, key in enumerate(table.keys()):
                table[key][attr] = attr.lower() if attr in self.decompositions[key] else attr.lower() + str(
                    index + 1)
        # print("Initial Tuples:")
        return table

    def apply_functional_dependencies(self, fd: list) -> tuple[None, str] | tuple[Any | None, Any, Any, str]:
        """
        Process each fd as in current iteration. Find two tuple with same x, make y the same
        :param fd:
        :return: modified table
        """
        x_attributes, y_attribute = fd
        rows_with_same_attributes = None
        seen_attribute_values = {}
        output_str = ''
        output_str += f"\nMatching two rows with same attributes '{x_attributes}'...\n"
        # print(f"Matching two rows with same attributes '{x_attributes}'...")
        for key, row in self.table.items():
            attribute_values = tuple(row.get(attr) for attr in x_attributes)
            if attribute_values in seen_attribute_values:
                matching_key = seen_attribute_values[attribute_values]
                matching_row = self.table[matching_key]
                rows_with_same_attributes = (matching_key, matching_row, key, row)
                break
            else:
                seen_attribute_values[attribute_values] = key

        # no two rows with same x_attributes value
        if not rows_with_same_attributes:
            output_str += f"No matching rows with same attributes '{x_attributes}' is found\n"
            # print(f"No matching rows with same attributes '{x_attributes}' is found")
            return None, output_str
        # print(f"Row 1: {matching_key}, Row 1 values: {matching_row}")
        # print(f"Row 2: {key}, Row 2 values: {row}")
        output_str += f"Found matching rows with same attributes '{x_attributes}', make their attribute '{y_attribute}' the same"
        # print(f"Found matching rows with same attributes '{x_attributes}', make their attribute '{y_attribute}' the same")
        # print the two rows with same attributes
        matching_key, matching_row, key, row = rows_with_same_attributes

        y_value1 = self.table[matching_key][y_attribute]
        y_value2 = self.table[key][y_attribute]

        # if y_value1 and y_value2 both have subscript, make second value same as first value
        # if one y_attribute value has not subscript, make two value no subscript
        has_subscript1 = self.check_if_str_has_subscript(y_value1)
        has_subscript2 = self.check_if_str_has_subscript(y_value2)

        # y_value1 and y_value2 both have subscript
        updated_row_key = None
        if has_subscript1 and has_subscript2:
            self.table[key][y_attribute] = y_value1
            updated_row_key = key
        # y_value1 has subscript and y_value2 has no subscript
        elif has_subscript1 and not has_subscript2:
            self.table[matching_key][y_attribute] = y_value2
            updated_row_key = matching_key
        # y_value1 has no subscript and y_value2 has subscript
        elif not has_subscript1 and has_subscript2:
            self.table[key][y_attribute] = y_value1
            updated_row_key = key
        return updated_row_key, output_str

    def return_table(self) -> str:
        """
        Print tuple table pretty
        +-----------------+-----+-----+-----+
        | Decomposition   | A   | B   | C   |
        +=================+=====+=====+=====+
        | R1(A, C)        | a   | b1  | c   |
        +-----------------+-----+-----+-----+
        | R2(B, C)        | a2  | b   | c   |
        +-----------------+-----+-----+-----+
        :return:
        """
        keys = list(self.table.keys())
        values = list(self.table.values())
        headers = ['Decomposition'] + sorted(values[0].keys())
        table = []
        for key, value in zip(keys, values):
            row = [key] + [value[attr] for attr in sorted(value.keys())]
            table.append(row)
        return tabulate(table, headers, tablefmt="grid")

    def chase_generator(self):
        # Start iterations
        for i, fd in enumerate(self.functional_dependencies):
            # print("\nApplying the {} Functional Dependencies: {} -> {}".format(i + 1, fd[0], fd[1]))
            a = "\nApplying the {} Functional Dependencies: {} -> {}".format(i + 1, fd[0], fd[1])
            yield a
            result_all = self.apply_functional_dependencies(fd)
            result = result_all[0]
            output_str = result_all[1]
            yield output_str
            if not result:
                # print("\nFunctional Dependency is violated, lossy decomposition!!!")
                b = "\nFunctional Dependency is violated, lossy decomposition!!!"
                yield b
                break

            updated_row_key = result
            c = "\nTuples after Applying Functional Dependencies:"
            # print("\nTuples after Applying Functional Dependencies:")
            d = self.return_table()
            yield c, d

            # check if updated row has no subscript at all
            if updated_row_key:
                no_subscript = True
                updated_row = self.table[updated_row_key]  # {'A': 'a', 'B': 'b', 'C': 'c'}
                for value in updated_row.values():
                    if self.check_if_str_has_subscript(value):
                        no_subscript = False
                        break
                if no_subscript:
                    e = "\nCongrats! No violation found in decompositions! Decomposition is lossless!!!"
                    yield e
                    # print("\nCongrats! No violation found in decompositions! Decomposition is lossless!!!")
                    break


    @staticmethod
    def input_attributes(num_attributes) -> list:
        num_attributes = int(num_attributes)
        attributes = [chr(ord('A') + i) for i in range(num_attributes)]
        # print("Attributes list: {}".format(', '.join(attributes)))
        return attributes

    @staticmethod
    def input_functional_dependencies(dependency) -> list[list]:
        functional_dependencies_input = dependency
        functional_dependencies_list = functional_dependencies_input.split(",")
        functional_dependencies = []
        for fd in functional_dependencies_list:
            fd = fd.split("->")
            fd = [f.strip() for f in fd]
            functional_dependencies.append(fd)
        return functional_dependencies

    @staticmethod
    def input_decompositions(decomposition) -> dict[Any, list[Any]]:
        decompositions_input = decomposition
        decomposition_matches = re.findall(r'(\w+)\((.*?)\)', decompositions_input)
        decompositions = {}
        for match in decomposition_matches:
            key = match[0].strip() + "(" + match[1].strip() + ")"
            values = [v.strip() for v in match[1].split(",")]
            decompositions[key] = values
        return decompositions

    @staticmethod
    def check_if_str_has_subscript(string: str) -> bool:
        matches = re.match(r"([a-zA-Z]+)(\d*)", string)
        digit_part1 = matches.group(2)
        return True if digit_part1 else False

class Model:
    def __init__(self):
        self.inp1 = 0
        self.inp2 = ''
        self.inp3 = ''
        self.checker = None
        self.tuples = {}
        self.attributes = []
        self.functional_dependencies = []
        self.decompositions = {}


class View:
    def __init__(self, root, model, save_data, handle_start_process_click):
        self.second_txt = None
        self.second_frame = None
        self.root = root
        self.model = model
        self.save_data = save_data
        self.handle_start_process_click = handle_start_process_click
        my_font = ("Arial", 12)
        self.main_frame = Frame(root)
        self.lb1 = Label(self.main_frame, text='Please enter the number of attributes', font=my_font)

        self.lb1.pack()
        self.inp1 = Entry(self.main_frame)
        self.inp1.pack()
        self.lb2 = Label(self.main_frame,
                    text='Please enter the functional dependencies separated by \',\' (e.g. B->E,EF->C,BC->A,AD->E)',
                    font=my_font)

        self.lb2.pack()
        self.inp2 = Entry(self.main_frame)
        self.inp2.pack()
        self.lb3 = Label(self.main_frame,
                    text="Please enter the desired decompositions separated by ',' (e.g. R1(A,B,C,F),R2(A,D,E),R3(B,D,F))",
                    font=my_font)
        self.lb3.pack()
        self.inp3 = Entry(self.main_frame)
        self.inp3.pack()

        self.main_button = Button(self.main_frame, text="OK", command=self.handle_button_click)
        self.main_button.pack()
        self.main_frame.pack()
    def handle_button_click(self):
        inp1 = self.inp1.get()
        inp2 = self.inp2.get()
        inp3 = self.inp3.get()
        self.model.inp1 = inp1
        self.model.inp2 = inp2
        self.model.inp3 = inp3
        self.save_data()
        self.main_frame.pack_forget()
        self.second_frame = Frame(self.root)
        second_label = Label(self.second_frame, text="Let's try!")
        second_button = Button(self.second_frame, text="Start Chase Algorithm", command=self.handle_start_process_click)
        second_label.pack()
        second_button.pack()
        self.second_txt = Text(self.second_frame, width=80, height=40)

        a = "Attributes list: {}".format(', '.join(self.model.attributes))
        self.second_txt.insert(END, a + '\n')
        b = "Initial Tuples:"
        self.second_txt.insert(END, b + '\n')
        c = self.model.checker.return_table()
        self.second_txt.insert(END, c)
        self.second_txt.pack()
        self.second_frame.pack()


class Controller:
    def __init__(self, root, model):
        self.model = model
        self.view = View(root, model, self.save_data, self.handle_start_process_click)
        self.generator = None
        self.running = True
        self.start_process = None

    def handle_start_process_click(self):
        if self.start_process:
            messagebox.showinfo("Info", "Already started!")
            return
        next_step_button = Button(self.view.second_frame, text='Next Step', command=self.next_step)
        next_step_button.pack()
        self.start_process = True
        checker = self.model.checker
        self.generator = checker.chase_generator()
        self.running = True

    def next_step(self):
        if self.running:
            try:
                next_value = next(self.generator)
                if type(next_value) == tuple:
                    self.view.second_txt.insert(END, next_value[0] + '\n')
                    self.view.second_txt.insert(END, next_value[1] + '\n')
                    self.view.second_txt.see(END)
                else:
                    self.view.second_txt.insert(END, next_value + '\n')
                    self.view.second_txt.see(END)
            except StopIteration:
                self.running = False
                messagebox.showinfo("Info", "process completed!")
        elif self.running is False:
            messagebox.showinfo("Info", "process completed!")
    def save_data(self):
        num_attributes = self.model.inp1
        dependency = self.model.inp2
        decomposition = self.model.inp3
        checker = LosslessDecompositionChecker(num_attributes, dependency, decomposition)
        self.model.checker = checker
        self.model.tuples = checker.table
        self.model.attributes = checker.attributes
        self.model.functional_dependencies = checker.functional_dependencies
        self.model.decompositions = checker.decompositions


if __name__ == "__main__":
    root = Tk()

    root.geometry('1280x650')
    root.title('The Chase Algorithm')
    model = Model()
    app = Controller(root, model)
    root.mainloop()