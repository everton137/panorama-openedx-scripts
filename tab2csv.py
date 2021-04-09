#!/usr/bin/env python

import csv
import sys


tab_in = csv.reader(open(sys.stdin, mode='rU'), dialect=csv.excel_tab)
comma_out = csv.writer(sys.stdout, delimiter=',', doublequote=False, escapechar='\\')

for row in tab_in:
    comma_out.writerow(row)

