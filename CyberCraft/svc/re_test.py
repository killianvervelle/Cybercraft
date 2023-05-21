import re

ram = "Ripjaws 4 DDR4 2400 C14 8x16GB"

match = re.search(r'(\d+)x(\d+)GB', ram)

if match:
    value1 = int(match.group(1))
    value2 = int(match.group(2))
    print(value1, value2)
else:
    print("No match")