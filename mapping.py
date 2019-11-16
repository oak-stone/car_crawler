#!/usr/bin/python3
def make_to_number(make):
    make = make.lower()
    if make == 'ducati':
        return 359
    elif make == 'infiniti':
        return 255
    elif make == 'volvo':
        return 10
    else:
        return None
