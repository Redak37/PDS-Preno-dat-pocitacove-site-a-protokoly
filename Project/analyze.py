import datetime
from statistics import stdev
import sys
from analyze_func import *


rows = list()
try:
    rows = get_rows(sys.argv[1])
except IndexError:
    print("Missing input csv file")
    sys.exit(1)
except FileNotFoundError:
    print(sys.argv[1], ": File not found")
    sys.exit(1)

rows_ctrl = rows[len(rows) * 2 // 3:]
rows = rows[:len(rows) * 2 // 3]

row_last = rows[-1][0]
time_zero = float(rows[0][0])
time_zero_ctrl = float(rows_ctrl[0][0])
time_end_ctrl = float(rows_ctrl[-1][0])
packets = list()

time_window = 300
try:
    time_w = float(sys.argv[2])
    if time_w > 0:
        time_window = time_w
except (IndexError, ValueError):
    pass

ftm, intervals = parse_rows(rows, time_window)
_, intervals_ctrl = parse_rows(rows_ctrl, time_window)
candidates = get_candidates(ftm)

stats = dict()
for key in intervals:
    for x in candidates[key]:
        small = list()
        big = list()
        for values in intervals[key]:
            small.append([v[0] for v in values if v[0] <= x])
            big.append([v[0] for v in values if v[0] > x])

        small_cnt = [len(values) for values in small]
        big_cnt = [len(values) for values in big]
        avg_small = sum(small_cnt) / len(small_cnt)
        avg_big = sum(big_cnt) / len(big_cnt)
        stdev_small = stdev(small_cnt)
        stdev_big = stdev(big_cnt)
        if key not in stats:
            if avg_small - 3 * stdev_small > 0:
                stats[key] = (x, avg_small, stdev_small, "small", avg_big, stdev_big, "big")
            if avg_big - 3 * stdev_big > 0 and (key not in stats or stdev_big < stats[key][1]):
                stats[key] = (x, avg_big, stdev_big, "big", avg_small, stdev_small, "small")
        else:
            if avg_small - 3 * stdev_small > 0 and stdev_small < stats[key][1]:
                stats[key] = (x, avg_small, stdev_small, "small", avg_big, stdev_big, "big")
            if avg_big - 3 * stdev_big > 0 and stdev_big < stats[key][1]:
                stats[key] = (x, avg_big, stdev_big, "big", avg_small, stdev_small, "small")

rows.sort(key=lambda k: k[-1])
rows_len = len(rows)
rows_ftm = dict()
size_candidates = dict()
for key in ftm:
    rows_ftm[key] = [row for row in rows if (row[1], row[2]) == key]
    rows_ftm[key].sort(key=lambda k: k[-1])
    rows_len = len(rows_ftm[key])
    size_candidates[key] = [
        int(rows_ftm[key][round(rows_len * 0.25) - 1][-1]),
        int(rows_ftm[key][round(rows_len * 0.5) - 1][-1]),
        int(rows_ftm[key][round(rows_len * 0.75) - 1][-1]),
        sum([int(r[-1]) for r in rows_ftm[key]]) / rows_len,
        (sum([int(r[-1]) * int(r[-1]) for r in rows_ftm[key]]) / rows_len) ** 0.5
    ]


stats_size = dict()
for key in intervals:
    for x in size_candidates[key]:
        small = list()
        big = list()
        for values in intervals[key]:
            small.append([v[-1] for v in values if v[-1] <= x])
            big.append([v[-1] for v in values if v[-1] > x])

        small_cnt = [len(values) for values in small]
        big_cnt = [len(values) for values in big]
        avg_small = sum(small_cnt) / len(small_cnt)
        avg_big = sum(big_cnt) / len(big_cnt)
        stdev_small = stdev(small_cnt)
        stdev_big = stdev(big_cnt)
        # print(key, x, avg_small, avg_big, stdev_small, stdev_big)
        if key not in stats_size:
            if avg_small - 3 * stdev_small > 0:
                stats_size[key] = (x, avg_small, stdev_small, "small", avg_big, stdev_big, "big")
            if avg_big - 3 * stdev_big > 0 and (key not in stats or stdev_big < stats[key][1]):
                stats_size[key] = (x, avg_big, stdev_big, "big", avg_small, stdev_small, "small")
        else:
            if avg_small - 3 * stdev_small > 0 and stdev_small < stats[key][1]:
                stats_size[key] = (x, avg_small, stdev_small, "small", avg_big, stdev_big, "big")
            if avg_big - 3 * stdev_big > 0 and stdev_big < stats[key][1]:
                stats_size[key] = (x, avg_big, stdev_big, "big", avg_small, stdev_small, "small")

# print(stats_size)
for key in stats:
    print(
        "(src, dst):", key, "type:", stats[key][3],
        ", line:", stats[key][0],
        "average:", stats[key][1],
        "stdev:", stats[key][2]
    )
printed_error = False
for key in intervals_ctrl:
    try:
        x = stats[key][0]
    except KeyError:
        continue
    y = 0
    z = 0
    err = 0
    errors = [False, False, False]
    errors2 = [False, False, False, False, False, False, False, False, False]
    vals = [stats[key][1], stats[key][1], stats[key][1]]

    for values in intervals_ctrl[key]:
        if stats[key][3] == "big":
            y = len([v[0] for v in values if v[0] > x])
        else:
            y = len([v[0] for v in values if v[0] <= x])

        if values == intervals_ctrl[key][-1]:
            y = y * time_window / (time_end_ctrl - time_zero_ctrl - err * time_window)

        vals[err % 3] = y
        if y < stats[key][1] - 3 * stats[key][2] or y > stats[key][1] + 3 * stats[key][2]:
            errors[err % 3] = True
            errors2[err % 9] = True
            print("Warning: src, dst:", key,
                  "Time Window:", datetime.datetime.fromtimestamp(err * time_window + time_zero), "+", time_window, "seconds,",
                  "number of packet:", y,
                  "Limits:", stats[key][1] - 3 * stats[key][2], stats[key][1] + 3 * stats[key][2])
        else:
            errors[err % 3] = False
            errors2[err % 9] = False

        if sum(errors) >= 2 or sum(errors2) >= 3 \
            or sum(vals) / 3 > stats[key][1] + 3 * stats[key][2] \
            or sum(vals) / 3 < stats[key][1] - 3 * stats[key][2]:
            print("Error: src, dst:", key,
                  "Time Window:", datetime.datetime.fromtimestamp(err * time_window + time_zero), "+", time_window, "seconds,",
                  "number of packet: (", vals[err % 3], ")", vals,
                  "Limits:", stats[key][1] - 3 * stats[key][2], stats[key][1] + 3 * stats[key][2])
            printed_error = True
        """
        if key in stats_size:
            if stats_size[key][3] == "big":
                z = len([v[0] for v in values if v[0] > x])
            else:
                z = len([v[0] for v in values if v[0] <= x])

            if z < stats_size[key][1] - 3 * stats_size[key][2] or z > stats_size[key][1] + 3 * stats_size[key][2]:
                print(key, err, z, stats_size[key][1] - 3 * stats_size[key][2], stats_size[key][1] + 3 * stats_size[key][2])
        """
        err += 1

if not printed_error:
    print("No errors")
