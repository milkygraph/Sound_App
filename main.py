import math
import tkinter

import numpy as np
import matplotlib.axes
import matplotlib.ticker
import ttkbootstrap as ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
from tkinter import messagebox
import re


class RegisterHandler:
    def __init__(self):
        pass


    # read the register file in text format and return the EQ values in a list
    def read_register_file(self):
        try:
            file_path = filedialog.askopenfilename(title="Select Register File", filetypes=[("Text Files", "*.txt")])
        except:
            return

        with open(file_path, "r") as file:
            lines = file.readlines()

            filters, frequencies, gains, qs = self.parse_filters(lines)

            RAM1_TAB = {}
            RAM2_TAB = {}

            for i in range(len(lines)):
                if "Ram1_Table" in lines[i]:
                    while lines[i] != "\n":
                        i += 1
                        RAM1_TAB[lines[i][5:7]] = lines[i][10:16]

            for i in range(len(lines)):
                if "Ram2_Mode" in lines[i]:
                    while lines[i] != "\n":
                        i += 1
                        RAM2_TAB[lines[i][5:7]] = lines[i][10:16]

        return RAM1_TAB, filters, frequencies, gains, qs

    def parse_filters(self, lines):
        i = 0
        pattern = '[\d.]+'
        while "Filters" not in lines[i]:
            i += 1

        i += 3
        filters = []
        frequencies = []
        gains = []
        qs = []

        for j in range(15):
            # filters.append(re.search(pattern, lines[i]).group())
            # i += 1
            # frequencies.append(re.search(pattern, lines[i]).group())
            # i += 1
            # gains.append(re.search(pattern, lines[i]).group())
            # i += 1
            # qs.append(re.search(pattern, lines[i]).group())
            # i += 1
            match = re.search(pattern, lines[i]).group()
            filters.append(match)
            i += 1

            match = re.search(pattern, lines[i]).group()
            frequencies.append(match)
            i += 1

            match = re.search(pattern, lines[i]).group()
            gains.append(match)
            i += 1

            match = re.search(pattern, lines[i]).group()
            qs.append(match)
            i += 1



        return filters, frequencies, gains, qs


def validate_entry(value):
    if value == "":
        return True

    try:
        float(value)
        return True
    except ValueError:
        return False


class UI:
    def __init__(self):

        self.data_hz = []
        self.data_spl = []
        self.reference_hz = []
        self.reference_spl = []

        self.root = ttk.Window("Sound", themename="darkly")
        self.root.geometry("800x600")

        self.root.bind("<Configure>", self.on_window_resize)

        self.graph_frame = ttk.Frame(self.root)
        self.graph_frame.grid(row=0, column=0, sticky=ttk.NSEW)

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=2, column=0, sticky=ttk.NSEW)

        self.fig = plt.figure()
        self.fig.set_facecolor("#222222")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#222222")
        self.ax.set_xlabel("Hz", color="white")
        self.ax.set_ylabel("SPL", color="white")
        self.ax.set_xscale('log')
        self.ax.set_xticks([20, 50, 100, 200, 500, 700, 1000, 1500, 2000, 3000, 4000, 5000, 7000, 10000,
                            13000, 17000, 20000])
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.get_xaxis().set_major_formatter(matplotlib.ticker.EngFormatter())

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=ttk.NSEW)

        self.filters_frame = ttk.Frame(self.root)
        self.filters_frame.grid(row=1, sticky=ttk.NSEW)

        self.filters = []
        self.entries = []
        self.gains = []
        self.qs = []
        self.filter_vars = []
        self.frequency_vars = []
        self.gain_vars = []
        self.q_vars = []

        self.entries = []

        vcmd = (self.root.register(validate_entry), '%P')
        filter_types = ["Flat", "High Pass", "Low Shelf", "Peak", "High Shelf", "Low Pass", "Notch"]
        column = 0
        while column < 16:
            ttk.Label(self.filters_frame, text=f"Filter {int(column / 2)}", width=10).grid(row=0, column=column, sticky=ttk.W)
            self.filters.append(ttk.StringVar(value=filter_types[0]))
            self.entries.append(ttk.OptionMenu(self.filters_frame, self.filters[int(column / 2)], *filter_types).grid(row=0, column=column+1, sticky=ttk.W))

            ttk.Label(self.filters_frame, text="Frequency", width=10).grid(row=1, column=column, sticky=ttk.W)
            self.entries.append(ttk.Entry(self.filters_frame, width=10, validate="focusout", validatecommand=vcmd).grid(row=1, column=column + 1, sticky=ttk.W))

            ttk.Label(self.filters_frame, text="Gain", width=10).grid(row=2, column=column, sticky=ttk.W)
            self.entries.append(ttk.Entry(self.filters_frame, width=10, validate="focusout", validatecommand=vcmd).grid(row=2, column=column + 1, sticky=ttk.W))

            ttk.Label(self.filters_frame, text="Q", width=10).grid(row=3, column=column, sticky=ttk.W)
            self.entries.append(ttk.Entry(self.filters_frame, width=10, validate="focusout", validatecommand=vcmd).grid(row=3, column=column + 1, sticky=ttk.W))
            column += 2

        ttk.Label(self.filters_frame, text="", width=10).grid(row=4, columnspan=8, sticky=ttk.W)
        column = 0
        while column < 14:
            ttk.Label(self.filters_frame, text=f"Filter {int(column / 2 + 9)}", width=10).grid(row=5, column=column, sticky=ttk.W)
            self.filters.append(ttk.StringVar(value=filter_types[0]))
            self.entries.append(ttk.OptionMenu(self.filters_frame, self.filters[int((column+16)/2)], *filter_types).grid(row=5, column=column+1, sticky=ttk.W))

            ttk.Label(self.filters_frame, text="Frequency", width=10).grid(row=6, column=column, sticky=ttk.W)
            self.entries.append(ttk.Entry(self.filters_frame, width=10, validate="focusout", validatecommand=vcmd).grid(row=6, column=column + 1, sticky=ttk.W))

            ttk.Label(self.filters_frame, text="Gain", width=10).grid(row=7, column=column, sticky=ttk.W)
            self.entries.append(ttk.Entry(self.filters_frame, width=10, validate="focusout", validatecommand=vcmd).grid(row=7, column=column + 1, sticky=ttk.W))

            ttk.Label(self.filters_frame, text="Q", width=10).grid(row=8, column=column, sticky=ttk.W)
            self.entries.append(ttk.Entry(self.filters_frame, width=10, validate="focusout", validatecommand=vcmd).grid(row=8, column=column + 1, sticky=ttk.W))

            column += 2


        self.load_frame = ttk.Frame(self.main_frame)
        self.load_frame.grid(row=2, columnspan=3, sticky=ttk.W)
        self.load_frame.grid_columnconfigure(0, weight=1)
        self.load_frame.grid_columnconfigure(1, weight=1)

        self.reference_load_button = ttk.Button(self.load_frame, text="Load Reference", command=self.load_reference)
        self.data_load_button = ttk.Button(self.load_frame, text="Load Data", command=self.load_data)
        self.reference_load_button.grid(row=0, column=0, sticky=ttk.NSEW, pady=10)
        self.data_load_button.grid(row=0, column=1, sticky=ttk.NSEW, padx=10, pady=10)

        self.load_register = ttk.Button(self.load_frame, text="Load Register", command=self.load_register)
        self.load_register.grid(row=1, column=0, sticky=ttk.NSEW, pady=10)

        self.find_average_button = ttk.Button(self.load_frame, text="Find Average", command=self.find_average_line)
        self.find_average_button.grid(row=1, column=1, sticky=ttk.NSEW, padx=10, pady=10)

        self.main_frame.grid_rowconfigure(0, weight=1, uniform="labels")
        self.main_frame.grid_rowconfigure(1, weight=1, uniform="labels")

    def on_window_resize(self, event):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.graph_frame.grid_columnconfigure(0, weight=1)
        self.graph_frame.grid_rowconfigure(0, weight=2)

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def on_hz_change(self, value):
        for i in range(len(self.data_hz)):
            if abs(self.data_hz[i] - float(self.current_hz.get())) < 1:
                self.current_spl.set(self.data_spl[i])
                self.spl_label["text"] = f"SPL: {self.current_spl.get():.2f} dB"
                break

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def on_spl_change(self, spl_value):
        for i in range(len(self.data_hz)):
            if abs(self.data_hz[i] - float(self.current_hz.get())) < 1:
                self.data_spl[i] = self.current_spl.get()
                break

        # change the spl value of current hz of the reference
        for i in range(len(self.reference_hz)):
            if abs(self.reference_hz[i] - float(self.current_hz.get())) < 0.1:
                self.reference_spl[i] = self.current_spl.get()
                break

        # update the graph
        for line in self.ax.lines:
            if line.get_label() == "Data":
                line.set_ydata(self.data_spl)
                break

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        ans = messagebox.askokcancel("Quit", "Do you want to quit?")
        if ans:
            self.root.quit()

    @staticmethod
    def convert_data(path) -> (np.array, np.array):
        x = []
        y = []
        # read the file
        file = open(path, "r").read()

        # remove the comments
        data = file.split("\n")
        data = [line for line in data if not line.startswith("*")]

        for line in data:
            line = line.split("\t")
            if line[0] == '':
                continue

            _x = float(line[0])
            _y = float(line[1])

            x.append(_x)
            y.append(_y)

        return np.array(x), np.array(y)

    def update_graph(self):
        self.ax.set_xticks([20, 50, 100, 200, 500, 700, 1000, 1500, 2000, 3000, 4000, 5000, 7000, 10000,
                            13000, 17000, 20000])
        self.ax.get_xaxis().set_major_formatter(matplotlib.ticker.EngFormatter())

    def load_data(self):
        self.data_spl, self.data_hz = [], []
        for line in self.ax.lines:
            if line.get_label() == "Data":
                line.remove()

        try:
            path = filedialog.askopenfilename(title="Select Data File", filetypes=(("Text Files", "*.txt"),))
            self.data_hz, self.data_spl = self.convert_data(path)
        except:
            return

        self.ax.plot(self.data_hz, self.data_spl, color="red", markersize=10, label="Data")
        self.update_graph()
        plt.legend()
        self.canvas.draw()

    def load_reference(self):
        self.reference_spl, self.reference_hz = [], []
        for line in self.ax.lines:
            if line.get_label() == "Reference":
                line.remove()

        try:
            path = filedialog.askopenfilename(title="Select Reference File", filetypes=(("Text Files", "*.txt"),))
            self.reference_hz, self.reference_spl = self.convert_data(path)
        except:
            return

        self.ax.plot(self.reference_hz, self.reference_spl, color="green", markersize=10, label="Reference")
        self.update_graph()
        plt.legend()
        self.canvas.draw()

    @staticmethod
    def load_register():
        handler = RegisterHandler()
        table, filters, frequencies, gains, qs = handler.read_register_file()

        for i in range(len(frequencies)):
            ttk.Label(filters, text=f"Filter {filters[i]}").grid(row=0, column=i, sticky=ttk.NSEW)
            ttk.Label(filters, text=f"Frequency: {frequencies[i]}").grid(row=1, column=i, sticky=ttk.NSEW)
            ttk.Label(filters, text=f"Gain: {gains[i]}").grid(row=2, column=i, sticky=ttk.NSEW)
            ttk.Label(filters, text=f"Q: {qs[i]}").grid(row=3, column=i, sticky=ttk.NSEW)

        filters.grid(row=0, column=0, columnspan=3, sticky=ttk.NSEW)

    def find_average_line(self):
        if len(self.ax.lines) == 0:
            return

        for line in self.ax.lines:
            if line.get_label() == "Average":
                line.remove()

        mean = logarithmic_average(self.data_spl)

        print("average = ", mean)
        plt.axhline(y=mean, color="blue", linestyle="--", label="Average")
        self.canvas.draw()



def logarithmic_average(numbers):
    # Take the logarithm of each number using base 10 (you can change the base as needed)
    log_numbers = [math.log10(x) for x in numbers]

    # Compute the average of the logarithms
    log_average = sum(log_numbers) / len(log_numbers)

    # Transform the average back to the original scale by exponentiating it
    average = 10 ** log_average

    return average


if __name__ == "__main__":
    app = UI()
    app.run()





