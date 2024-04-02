"""
# Time       :2024/4/2 12:57
# Author     :Li Yijia
"""

from tkinter import *
from tkinter import messagebox

from ttkbootstrap import Style
from common import return_df_pretty
from chase_generator_distinguished_version import DistinguishedVariableChaseChecker


class Model:
    def __init__(self):
        self.choice = None
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
        self.third_txt = None
        self.second_frame = None
        self.inp1 = None
        self.inp2 = None
        self.inp3 = None
        self.sec_button = None
        self.reminder = None
        self.lb1 = None
        self.lb2 = None
        self.lb3 = None
        self.third_frame = None
        self.root = root
        self.model = model
        self.save_data = save_data
        self.handle_start_process_click = handle_start_process_click

        self.my_biggest_font = ("Arial", 16)
        self.my_sec_font = ("Arial", 14)

        self.main_frame = Frame(root)

        # add blank space
        for _ in range(4):
            Label(self.main_frame, text=" ").pack()

        select_lb = Label(self.main_frame, text='Let\'s play THE CHASE! Which game do you want to play?',
                          font=self.my_biggest_font)
        select_lb.pack()
        self.choice = IntVar()
        check_lossless_decomposition = Radiobutton(self.main_frame, text="check if your decomposition is lossless",
                                                   variable=self.choice, value=1, font=self.my_sec_font)

        check_lossless_decomposition.pack()
        check_dependency = Radiobutton(self.main_frame, text="check if your dependency can be satisfied",
                                       variable=self.choice, value=0, font=self.my_sec_font)
        check_dependency.pack()

        self.button_choice = Button(self.main_frame, text="OK", command=self.handle_first_choice,width=6,height=2)
        self.button_choice.pack()
        self.main_frame.pack()

    def handle_first_choice(self):
        self.model.choice = self.choice.get()
        self.main_frame.pack_forget()
        self.second_frame = Frame(self.root)
        # add blank space
        for _ in range(3):
            Label(self.second_frame, text=" ").pack()

        if self.choice.get() == 0:
            Label(self.second_frame, text='You selected chasing dependency!', font=self.my_biggest_font).pack()
        else:
            Label(self.second_frame, text='You selected lossless decomposition!', font=self.my_biggest_font).pack()

        self.lb1 = Label(self.second_frame, text='Please enter the number'
                                                 ' of attributes\n (press Enter key to see attributes generated)',
                         font=self.my_biggest_font)
        self.lb1.pack()
        self.inp1 = Entry(self.second_frame)
        self.inp1.pack()

        def forget(item):
            if item is not None:
                item.pack_forget()

        # Define a callback function to handle the event
        def on_inp1_enter(enter):
            attributes = [chr(ord('A') + i) for i in range(int(self.inp1.get()))]
            forget(self.reminder)
            forget(self.inp2)
            forget(self.lb2)
            forget(self.inp3)
            forget(self.lb3)
            forget(self.sec_button)

            self.reminder = Label(self.second_frame, text="Attributes list: {}".format(', '.join(attributes)),
                                  font=self.my_biggest_font)
            self.reminder.pack()
            self.lb2 = Label(self.second_frame,
                             text='Enter functional/multi-value dependencies separated by \';\' (e.g. A->>B,C;D->C):',
                             font=self.my_biggest_font)

            self.lb2.pack()
            self.inp2 = Entry(self.second_frame)
            self.inp2.pack()
            if self.choice.get() == 1:
                self.lb3 = Label(self.second_frame,
                                 text="Please enter desired decompositions separated by ';' (e.g. R1(A,B,D);R2(A,C))",
                                 font=self.my_biggest_font)
            elif self.choice.get() == 0:
                self.lb3 = Label(self.second_frame,
                                 text="Enter desired dependency (e.g. A->C)",
                                 font=self.my_biggest_font)
            self.lb3.pack()
            self.inp3 = Entry(self.second_frame)
            self.inp3.pack()
            for _ in range(1):
                Label(self.second_frame, text=" ").pack()

            self.sec_button = Button(self.second_frame, text="OK", command=self.handle_button_click, width=6, height=2)
            self.sec_button.pack()

        # Bind the callback function to the <FocusOut> event of inp1
        self.inp1.bind("<Return>", on_inp1_enter)
        self.second_frame.pack()

    def handle_button_click(self):
        inp1 = self.inp1.get()
        inp2 = self.inp2.get()
        inp3 = self.inp3.get()
        self.model.inp1 = inp1
        self.model.inp2 = inp2
        self.model.inp3 = inp3
        self.save_data()
        # self.main_frame.pack_forget()
        self.second_frame.pack_forget()
        self.third_frame = Frame(self.root)
        # add blank space
        for _ in range(1):
            Label(self.third_frame, text=" ").pack()
        third_label = Label(self.third_frame, text="Let's try!", font=self.my_biggest_font)
        third_button = Button(self.third_frame, text="Start Chase Algorithm", command=self.handle_start_process_click,font=self.my_sec_font)
        third_label.pack()
        third_button.pack()

        self.third_txt = Text(self.third_frame, width=100, height=30, font=('Arial', 10))

        a = "Attributes list: {}".format(', '.join(self.model.attributes))
        self.third_txt.insert(END, a + '\n')
        b = "Initial Tuples:"
        self.third_txt.insert(END, b + '\n')
        c = return_df_pretty(self.model.checker.table)
        self.third_txt.insert(END, c)
        self.third_txt.pack()
        self.third_frame.pack()


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
        next_step_button = Button(self.view.third_frame, text='Next Step', command=self.next_step,font=("Arial", 16))
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
                    self.view.third_txt.insert(END, next_value[0] + '\n')
                    self.view.third_txt.insert(END, next_value[1] + '\n')
                    self.view.third_txt.see(END)
                else:
                    self.view.third_txt.insert(END, next_value + '\n')
                    self.view.third_txt.see(END)
            except StopIteration:
                self.running = False
                messagebox.showinfo("Info", "process completed!")
                # Button(self.view.third_frame, text="OK", command=self.handle_return_click, width=6, height=2).pack()
        elif self.running is False:
            messagebox.showinfo("Info", "process completed!")
    # def handle_return_click(self):
    #     self.view.third_frame.pack_forget()
    #     self.model = Model()
    #     self.generator = None
    #     self.running = True
    #     self.start_process = None
    #     self.view = View(root, model, self.save_data, self.handle_start_process_click)
    def save_data(self):
        num_attributes = int(self.model.inp1)
        dependency = self.model.inp2
        input_desired_decompositions_dependency = self.model.inp3
        attributes = [chr(ord('A') + i) for i in range(num_attributes)]
        checker = DistinguishedVariableChaseChecker(self.model.choice, attributes, dependency,
                                                    input_desired_decompositions_dependency)
        self.model.checker = checker
        self.model.tuples = checker.table
        self.model.attributes = checker.attributes
        self.model.choice = checker.option
        self.model.functional_dependencies = checker.dependencies
        self.model.desired_decompositions = checker.desired_decompositions if checker.option == 1 else None
        self.model.desired_dependency = checker.desired_dependency if checker.option == 0 else None


if __name__ == "__main__":
    root = Tk()
    style = Style()
    style = Style(theme='sandstone')
    TOP6 = style.master

    root.geometry('1280x650')
    root.title('The Chase Algorithm')
    model = Model()
    app = Controller(root, model)
    root.mainloop()
