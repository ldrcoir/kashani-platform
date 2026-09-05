#!/usr/bin/env python3
"""
Generate series A136030 from number 1 to 8000.
Each line: A136030-NNNN (4-digit zero-padded)
Output: text file in /home/z/my-project/download/
"""

OUTPUT_PATH = "/home/z/my-project/download/A136030_series_1_to_8000.txt"
PREFIX = "A136030"
START = 1
END = 8000

def main():
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for i in range(START, END + 1):
            f.write(f"{PREFIX}-{i:04d}\n")
    # Verify
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"File written: {OUTPUT_PATH}")
    print(f"Total lines: {len(lines)}")
    print(f"First line: {lines[0].strip()}")
    print(f"Last line:  {lines[-1].strip()}")

if __name__ == "__main__":
    main()
