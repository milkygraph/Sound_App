import numpy as np


class Analyzer:
    def __init__(self):
        pass

    @staticmethod
    def load_data(filename: str) -> (np.ndarray, np.ndarray):
        """
        Reads file and returns lists of hertz and db values
        :param filename:
        :return hz: list of hertz values db: list of db values
        """
        hz = []
        db = []

        with open(filename, 'r') as f:
            f = f.read()
            f = f.split('\n')
            f = [line for line in f if not line.startswith('*')]

            for line in f:
                line = line.split('\t')
                if line[0] == '':
                    continue

                hz.append(float(line[0]))
                db.append(float(line[1]))

        return np.array(hz), np.array(db)


    @staticmethod
    def find_indices(arr: np.ndarray, start, end) -> (int, int):
        end_index = 0
        start_index = 0
        while end_index < len(arr):
            if arr[end_index] <= start:
                start_index = end_index

            if arr[end_index] >= end:
                break
            end_index += 1

        return start_index, end_index

    @staticmethod
    def find_average(db: np.ndarray, hz: np.ndarray, average_start: int = 100, average_end: int = 7000,
                     average_correction: float = 10.0) -> (float, float):
        """
        Finds the average line of the data
        :param db: list of db values
        :param hz: list of hertz values
        :param average_start: hertz value to start averaging
        :param average_end: hertz value to end averaging
        :param average_correction: correction factor for the average line
        :return: slope and y-intercept of the average line
        """

        # filter data according to the average start and end values
        start_index, end_index = Analyzer.find_indices(hz, average_start, average_end)

        # decrease the spl value of the data logarithmically after average_end hz
        for i in range(end_index, len(db)):
            db[i] += average_correction * np.log10(hz[i] / average_end)

        return db[start_index:end_index].mean()
