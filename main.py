import numpy as np
import matplotlib.axes
import matplotlib.ticker
import ttkbootstrap as ttk
import matplotlib.pyplot as plt
from validators import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
from tkinter import messagebox
from analyzer import Analyzer
from registers import RegisterHandler


class UI:
    def __init__(self):
        self.average_correction = 20
        self.diff_graph = None
        self.data_hz = []
        self.data_spl = []
        self.reference_hz = []
        self.reference_spl = []
        self.data_spl_average = 0
        self.threshold = 3

        self.root = ttk.Window("Sound", themename="flatly")
        self.root.geometry("800x600")

        self.root.bind("<Configure>", self.on_window_resize)

        bg_color = ttk.Style().lookup("TFrame", "background")
        fg_color = ttk.Style().lookup("TFrame", "foreground")

        self.graph_frame = ttk.Frame(self.root)
        self.graph_frame.grid(row=0, column=0, sticky=ttk.NSEW)

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=2, column=0, sticky=ttk.NSEW)

        self.fig = plt.figure()
        self.fig.set_facecolor(bg_color)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(bg_color)
        self.ax.set_xlabel("Hz", color=fg_color)
        self.ax.set_ylabel("SPL", color=fg_color)
        self.ax.set_xscale('log')
        self.ax.set_xticks([20, 50, 100, 200, 500, 700, 1000, 1500, 2000, 3000, 4000, 5000, 7000, 10000,
                            13000, 17000, 20000])
        self.ax.tick_params(axis='x', colors=fg_color)
        self.ax.tick_params(axis='y', colors=fg_color)
        self.ax.get_xaxis().set_major_formatter(matplotlib.ticker.EngFormatter())
        self.ax.grid(True, color=fg_color, alpha=0.2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=ttk.NSEW)

        self.load_frame = ttk.Frame(self.main_frame)
        self.load_frame.grid(row=2, columnspan=3, sticky=ttk.W)
        self.load_frame.grid_columnconfigure(0, weight=1)
        self.load_frame.grid_columnconfigure(1, weight=1)

        # Row 0: Load Reference, Load Data
        self.reference_load_button = ttk.Button(self.load_frame, text="Load Reference", command=self.load_reference)
        self.data_load_button = ttk.Button(self.load_frame, text="Load Data", command=self.load_data)
        self.reference_load_button.grid(row=0, column=0, sticky=ttk.NSEW, padx=10, pady=10)
        self.data_load_button.grid(row=0, column=1, sticky=ttk.NSEW, pady=10)

        self.load_register = ttk.Button(self.load_frame, text="Load Register", command=self.load_register)
        self.load_register.grid(row=0, column=2, sticky=ttk.NSEW, padx=10, pady=10)

        # Row 1: Average, Deviation, Threshold
        self.find_average_button = ttk.Button(self.load_frame, text="Find Average", command=self.find_average_line)
        self.find_average_button.grid(row=1, column=0, sticky=ttk.NSEW, padx=10, pady=10)

        self.threshold_slider = ttk.Scale(self.load_frame, from_=0, to=10, orient=ttk.HORIZONTAL,
                                          command=self.on_threshold_change)
        self.threshold_slider.grid(row=1, column=1, sticky=ttk.NSEW, padx=10, pady=10)

        self.threshold_label = ttk.Label(self.load_frame, text="Threshold: {:.2f}".format(self.threshold))
        self.threshold_label.grid(row=1, column=2, sticky=ttk.NSEW, pady=10)

        self.show_diff_graph_button = ttk.Checkbutton(self.load_frame, text="Toggle Difference Graph",
                                                      command=self.toggle_diff_graph)
        self.show_diff_graph_button.grid(row=1, column=3, sticky=ttk.NSEW, pady=10)

        # Average Calculation
        self.average_start = ttk.IntVar()
        self.average_start.set(100)
        self.average_end = ttk.IntVar()
        self.average_end.set(13000)

        int_validate = (self.load_frame.register(validate_int), "%P")
        self.settings_frame = ttk.Frame(self.load_frame)
        self.settings_frame.grid(row=2, columnspan=4, rowspan=2, sticky=ttk.NSEW, padx=10, pady=10)

        self.average_start_label = ttk.Label(self.settings_frame, text="Average Start")
        self.average_start_label.grid(row=0, column=0, sticky=ttk.W, padx=10, pady=10)
        self.average_start_entry = ttk.Entry(self.settings_frame, textvariable=self.average_start, validate="key",
                                             validatecommand=int_validate)
        self.average_start_entry.grid(row=0, column=1, sticky=ttk.NSEW, padx=10, pady=10)

        self.average_end_label = ttk.Label(self.settings_frame, text="Average End")
        self.average_end_label.grid(row=0, column=2, sticky=ttk.W, padx=10, pady=10)
        self.average_end_entry = ttk.Entry(self.settings_frame, textvariable=self.average_end, validate="key",
                                           validatecommand=int_validate)
        self.average_end_entry.grid(row=0, column=3, sticky=ttk.NSEW, pady=10)

        self.average_start_entry.bind("<Return>", self.find_average_line)
        self.average_end_entry.bind("<Return>", self.find_average_line)

        self.diff_graph_start = ttk.IntVar(value=100)
        self.diff_graph_end = ttk.IntVar(value=20000)

        self.diff_graph_start_label = ttk.Label(self.settings_frame, text="Diff Graph Start")
        self.diff_graph_start_label.grid(row=1, column=0, sticky=ttk.W, padx=10, pady=10)
        self.diff_graph_start_entry = ttk.Entry(self.settings_frame, textvariable=self.diff_graph_start, validate="key",
                                                validatecommand=int_validate)
        self.diff_graph_start_entry.grid(row=1, column=1, sticky=ttk.NSEW, padx=10, pady=10)

        self.diff_graph_end_label = ttk.Label(self.settings_frame, text="Diff Graph End")
        self.diff_graph_end_label.grid(row=1, column=2, sticky=ttk.W, padx=10, pady=10)
        self.diff_graph_end_entry = ttk.Entry(self.settings_frame, textvariable=self.diff_graph_end, validate="key",
                                              validatecommand=int_validate)
        self.diff_graph_end_entry.grid(row=1, column=3, sticky=ttk.NSEW, pady=10)

        self.diff_graph_end_entry.bind("<Return>", self.show_diff_graph)
        self.diff_graph_start_entry.bind("<Return>", self.show_diff_graph)

        self.main_frame.grid_rowconfigure(0, weight=1, uniform="labels")
        self.main_frame.grid_rowconfigure(1, weight=1, uniform="labels")

    def on_window_resize(self, event=None):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.graph_frame.grid_columnconfigure(0, weight=1)
        self.graph_frame.grid_rowconfigure(0, weight=2)

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        ans = messagebox.askokcancel("Quit", "Do you want to quit?")
        if ans:
            self.root.quit()

    def update_graph(self):
        self.ax.set_xticks([20, 50, 100, 200, 500, 700, 1000, 1500, 2000, 3000, 4000, 5000, 7000, 10000,
                            13000, 17000, 20000])
        self.ax.get_xaxis().set_major_formatter(matplotlib.ticker.EngFormatter())

    def load_data(self):
        # Reset the data and associated graphs
        self.data_spl, self.data_hz = [], []
        for line in self.ax.lines:
            if line.get_label() == "Data":
                line.remove()

        # Load the data
        try:
            path = filedialog.askopenfilename(title="Select Data File", filetypes=(("Text Files", "*.txt"),))
            self.data_hz, self.data_spl = Analyzer.load_data(path)
        except Exception as e:
            print(e)
            return e

        if self.diff_graph is not None:
            self.find_average_line()

        # Plot
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
            self.reference_hz, self.reference_spl = Analyzer.load_data(path)
        except Exception as e:
            print(e)
            return e

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

    def find_average_line(self, value=None):
        if len(self.ax.lines) == 0:
            return

        for line in self.ax.lines:
            if line.get_label() == "Average":
                line.remove()

        self.data_spl_average = Analyzer.find_average(np.array(self.data_spl), np.array(self.data_hz),
                                                      self.average_start.get(), self.average_end.get(),
                                                      self.average_correction)
        self.show_diff_graph()

        print("average = ", self.data_spl_average)
        plt.axhline(y=self.data_spl_average, color="green", linestyle="--", label="Average")
        plt.legend()
        self.canvas.draw()

    def show_diff_graph(self, value=None):
        # compute the deviant parts of the graph
        start_frequency = self.diff_graph_start.get()
        end_frequency = self.diff_graph_end.get()

        start_index, end_index = Analyzer.find_indices(np.array(self.data_hz), start_frequency, end_frequency)

        deviation = np.abs(np.array(self.data_spl[start_index:end_index]) - self.data_spl_average)
        mask = deviation > float(self.threshold)

        if self.diff_graph is not None:
            self.diff_graph.remove()

        self.diff_graph = self.ax.fill_between(self.data_hz[start_index:end_index],
                                               self.data_spl[start_index:end_index], self.data_spl_average,
                                               where=mask, color="red", alpha=0.5, label="Deviant")
        plt.legend()
        self.canvas.draw()

    def toggle_diff_graph(self):
        if self.diff_graph is not None:
            self.diff_graph.set_visible(not self.diff_graph.get_visible())
        self.canvas.draw()

    def on_threshold_change(self, value):
        self.threshold = value
        self.threshold_label.config(text="Threshold: {:.2f}".format(float(value)))
        self.show_diff_graph()


if __name__ == "__main__":
    app = UI()
    app.run()
