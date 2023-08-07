from tkinter import filedialog
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

    @staticmethod
    def parse_filters(lines):
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

