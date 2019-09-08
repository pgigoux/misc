import re

STATE_START = 0
STATE_PACKAGE = 1

def read_deplist(file_name):
    try:
        f = open(file_name, 'r')
    except IOError as e:
        print e
        return

    state = STATE_START
    for line in f:
        words = line.split()
        print words
        if state == STATE_START:
            if words[0] == 'package:':
                package_name = words[1]
                state = STATE_PACKAGE
                print 'found package', package_name
        elif state == STATE_PACKAGE:
            if words[0] == 'dependency:':
                print 'found dependency', words[1]
                break

if __name__ == '__main__':
    read_deplist('deplist')