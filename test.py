#!/usr/bin/python3
import json
import os
import time
from time import sleep

SHA1_JSON = '#sha1.json'


def jsonNameWithTime():
    return '#sha1_' + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + '.json'


def min(l):
    l.sort(reverse=True)


t1 = jsonNameWithTime()
sleep(1)
t2 = jsonNameWithTime()

filenames = [t1, t2]

jsons = [filename for filename in filenames if filename.find(
    '#sha1_', 0, 5) == 0]

print(t1.find('#sha1_', 0, 6))

# print(t1)
# print(t2)

# Calculate the difference between two dictionaries as:
# (1) items added
# (2) items removed
# (3) keys same in both but changed values
# (4) keys same in both and unchanged values


class DictDiffer(object):
    def __init__(self, cnt_dict, past_dict):
        self.current_dict, self.past_dict = cnt_dict, past_dict
        self.cnt_set, self.past_set = set(
            cnt_dict.keys()), set(past_dict.keys())
        self.intersect = self.cnt_set.intersection(self.past_set)

    def added(self):
        return self.cnt_set - self.intersect

    def removed(self):
        return self.past_set - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])
