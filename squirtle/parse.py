import re


def parse_list(string):
    return re.findall("([A-Za-z]|-?[0-9]+\.?[0-9]*(?:e-?[0-9]*)?)", string)


def parse_style(string):
    sdict = {}
    for item in string.split(';'):
        if ':' in item:
            key, value = item.split(':')
            sdict[key] = value
    return sdict


def parse_color(c, default=None):
    if not c:
        return default
    if c == 'none':
        return None
    # Remove whitespace around string
    c = c.strip()
    if c[0] == '#':
        c = c[1:]
    try:
        if c.startswith('url(#'):
            return c[5:-1]
        elif c.startswith('rgb'):
            c = c[4:-1]
            r, g, b = [int(x.strip()) for x in c.split(",")]
        elif len(c) == 6:
            r = int(c[0:2], 16)
            g = int(c[2:4], 16)
            b = int(c[4:6], 16)
        elif len(c) == 3:
            r = int(c[0], 16) * 17
            g = int(c[1], 16) * 17
            b = int(c[2], 16) * 17
        else:
            raise Exception("Incorrect length for colour " + str(c) + " length " + str(len(c)))
        return [r, g, b, 255]
    except Exception as ex:
        print(f'Exception parsing color {ex}')
        return None
