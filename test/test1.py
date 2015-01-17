#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from multiprocessing import Queue, Process

class MyMegaException(Exception): pass

def deadlytask(queue):
    queue.put(MyMegaException("Kranty 6"))

def main():
    queue = Queue()
    task = Process(target=deadlytask, args=(queue,))
    task.start()
    while task.is_alive():
        data = queue.get()
        raise data

if __name__ == '__main__':
    main()
