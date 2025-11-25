#!/usr/bin/env python3
"""
Reorganize predictions.py routes to fix route ordering issue.
Moves /daily/* routes before /{ticker} route.
"""

# Read the file
with open('app/api/predictions.py', 'r') as f:
    lines = f.readlines()

# Find the line numbers
summary_start = None
ticker_start = None
daily_save_start = None

for i, line in enumerate(lines):
    if '@router.get("/summary")' in line:
        summary_start = i
    elif '@router.get("/{ticker}")' in line and ticker_start is None:
        ticker_start = i
    elif '@router.post("/daily/save")' in line:
        daily_save_start = i
        break

if not all([summary_start, ticker_start, daily_save_start]):
    print(f"Could not find all markers: summary={summary_start}, ticker={ticker_start}, daily={daily_save_start}")
    exit(1)

print(f"Found summary route at line {summary_start + 1}")
print(f"Found ticker route at line {ticker_start + 1}")
print(f"Found daily routes starting at line {daily_save_start + 1}")

# Extract daily routes (from daily_save_start to end of file)
daily_routes = lines[daily_save_start:]

# Remove daily routes from original position
lines_without_daily = lines[:daily_save_start]

# Insert daily routes before ticker route
new_lines = (
    lines_without_daily[:ticker_start] +
    daily_routes +
    ['\n'] +
    lines_without_daily[ticker_start:]
)

# Write back
with open('app/api/predictions.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Routes reorganized successfully!")
print(f"Daily routes moved from line {daily_save_start + 1} to line {ticker_start + 1}")
