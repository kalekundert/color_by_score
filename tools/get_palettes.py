#!/usr/bin/env python3

from more_itertools import unique_everseen

palette_ranges = {}
palette_names = [
        'blue_green',
        'blue_magenta',
        'blue_red',
        'blue_white_green',
        'blue_white_magenta',
        'blue_white_red',
        'blue_white_yellow',
        'blue_yellow',
        'cbmr',
        'cyan_magenta',
        'cyan_red',
        'cyan_white_magenta',
        'cyan_white_red',
        'cyan_white_yellow',
        'cyan_yellow',
        'gcbmry',
        'green_blue',
        'green_magenta',
        'green_red',
        'green_white_blue',
        'green_white_magenta',
        'green_white_red',
        'green_white_yellow',
        'green_yellow',
        'green_yellow_red',
        'magenta_blue',
        'magenta_cyan',
        'magenta_green',
        'magenta_white_blue',
        'magenta_white_cyan',
        'magenta_white_green',
        'magenta_white_yellow',
        'magenta_yellow',
        'rainbow',
        'rainbow2',
        'rainbow2_rev',
        'rainbow_cycle',
        'rainbow_cycle_rev',
        'rainbow_rev',
        'red_blue',
        'red_cyan',
        'red_green',
        'red_white_blue',
        'red_white_cyan',
        'red_white_green',
        'red_white_yellow',
        'red_yellow',
        'red_yellow_green',
        'rmbc',
        'yellow_blue',
        'yellow_cyan',
        'yellow_cyan_white',
        'yellow_green',
        'yellow_magenta',
        'yellow_red',
        'yellow_white_blue',
        'yellow_white_green',
        'yellow_white_magenta',
        'yellow_white_red',
        'yrmbcg',
]


for name in palette_names:
    colors = []
    cmd.spectrum('resi', name, 'all')
    cmd.iterate('all', 'colors.append(color)', space=locals())
    palette_ranges[name] = list(unique_everseen(colors))

with open('palettes.py', 'w') as file:
    file.write('palettes = {\n')
    for name, colors in palette_ranges.items():
        if colors == range(min(colors), max(colors) + 1):
            file.write("        '{}': range({}, {}),\n".format(name, min(colors), max(colors) + 1))
        else:
            file.write("        '{}': [{}],\n".format(name, ', '.join(map(str, colors))))
    file.write('}\n')

