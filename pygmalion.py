#!/usr/bin/env python

"""
pygmalion

Generate random gibberish based off a Markov model of input plain text
files. Only slightly smarter than a million chimps.
"""

import random
from pprint import pprint
from collections import deque

class Node(object):
    """Node in a tree"""
    def __init__(self, value):
        self.count = 0
        self.value = value
        self.children = {}
        return
    def get(self, key):
        try:
            return self.children[key]
        except KeyError:
            self.children[key] = Node(key)
        finally:
            return self.children[key]
    def __str__(self):
        return self.value
    def __cmp__(self, other):
        return cmp(self.count, other.count)

class MarkovModel(object):
    """Collect a k-th order Markov chain for English text"""
    def __init__(self, k):
        self.k = k
        self.n = 0
        self.counts = {}
        self.context = deque()
        return
    def witness(self, word):
        if len(self.context) < self.k:
            self.context.append(word)
            return
        self.context.popleft()
        inner = self.counts.setdefault(tuple(self.context), dict())
        try:
            inner[word] += 1
        except KeyError:
            inner[word] = 1
        self.n += 1
        self.context.append(word)
        return
    def sample(self, context):
        dist = []
        for value, count in self.counts[tuple(context)].items():
            dist.append((count, value))
        total = float(sum(w for w, v in dist))
        i = 0
        n = len(dist)
        weight, val = dist[0]
        x = total * (1 - random.random() ** (1.0 / n))
        total -= x
        while x > weight:
            x -= weight
            i += 1
            weight, val = dist[i]
        return val
    def pprint(self):
        pprint(self.counts)

def gibberish(model, prehistory):
    """Create a generator for Markov generated gibberish"""
    context = deque(prehistory)
    def gibberish_generator():
        for word in context:
            yield word
        while True:
            word = model.sample(context)
            context.append(word)
            if len(context) > model.k - 1:
                context.popleft()
            yield word
    return gibberish_generator()

def analyse(fobject, model, stripchars=None):
    """
    Analyse a file and extract probabilities for a k-th order Markov chain
    """
    delimeter = " "
    for line in fobject:
        words = line.split(delimeter)
        for word in words:
            word = word.strip(stripchars)
            if not word:
                continue
            model.witness(word)

if __name__ == '__main__':
    import sys
    try:
        fobject = open(sys.argv[1])
    except (IndexError, IOError):
        fobject = sys.stdin
    model = MarkovModel(5)
    analyse(fobject, model, stripchars=" \t\n")
