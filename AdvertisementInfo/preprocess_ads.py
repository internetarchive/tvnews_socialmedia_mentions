import re
import glob
import os
import csv

def parse_time(ts: str) -> float:
    """Convert hh:mm:ss,ms → seconds"""
    h, m, s_ms = ts.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def extract_segments(ttxt_file):
    segments = []
    current_start = None
    current_type = None
    prev_end = None

    with open(ttxt_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "|" not in line:
                continue

            start, end, mode, *_ = line.split("|", 3)
            seg_type = "news" if re.match(r"^RU", mode) else "ad"

            if current_type is None:
                # first line
                current_type = seg_type
                current_start = start

            elif seg_type != current_type:
                # type switched → close previous block
                duration = parse_time(prev_end) - parse_time(current_start)
                segments.append((current_type, current_start, prev_end, round(duration, 3)))
                current_type = seg_type
                current_start = start

            # if seg_type == current_type → continue extending block
            prev_end = end

    # close last open segment
    if current_type is not None and current_start is not None:
        duration = parse_time(prev_end) - parse_time(current_start)
        segments.append((current_type, current_start, prev_end, round(duration, 3)))

    return segments

def process_directory(path, output_csv):
    rows = []
    for file in glob.glob(path):
        episode = os.path.splitext(os.path.basename(file))[0]
        segs = extract_segments(file)
        for seg_type, start, end, dur in segs:
            rows.append((episode, seg_type, start, end, dur))

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["episode", "type", "start_time", "end_time", "duration"])
        writer.writerows(rows)

    print(f"✅ Segments written to {output_csv}")

if __name__ == "__main__":
    process_directory("SelectedEpisodes/*.ttxt", "ad_segments.csv")
