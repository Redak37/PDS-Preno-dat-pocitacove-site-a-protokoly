import csv


def get_rows(file):
    with open(file, 'r') as csvfile:
        return [r for r in csv.reader(csvfile)]


def get_candidates(ftm):
    cands = dict()
    for key in ftm.keys():
        ftm[key].sort(key=lambda k: k[0])
        length = len(ftm[key])
        """
        print(
            length,
            ftm[key][0],
            ftm[key][round(length * 0.25) - 1],
            ftm[key][round(length * 0.5) - 1],
            ftm[key][round(length * 0.75) - 1],
            ftm[key][-1],
            sum([v[0] for v in ftm[key]]) / length,
            (sum([v[0] * v[0] for v in ftm[key]]) / length) ** 0.5
        )
        """
        cands[key] = [
            ftm[key][round(length * 0.25) - 1][0],
            ftm[key][round(length * 0.5) - 1][0],
            ftm[key][round(length * 0.75) - 1][0],
            sum([v[0] for v in ftm[key]]) / length,
            (sum([v[0] * v[0] for v in ftm[key]]) / length) ** 0.5
        ]
    return cands


def parse_rows(rows, time_window):
    row_last = 0
    ftm = dict()
    intervals = dict()
    time_zero = float(rows[0][0])
    for row in rows:
        key = (row[1], row[2])
        if key not in ftm:
            ftm[key] = list()
            intervals[key] = list()

        row_now = float(row[0])

        if row_last != 0:
            ftm[key].append((row_now - row_last, row_now - time_zero))
            while len(intervals[key]) < (row_now - time_zero) / time_window:
                intervals[key].append(list())
            intervals[key][-1].append((row_now - row_last, int(row[-1])))

        row_last = row_now

    return ftm, intervals
