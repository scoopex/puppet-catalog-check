import os
import threading
import sys

from nose.tools import *

RUNDIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.path.append(RUNDIR + "/lib/")

from catalogtests.threads import ThreadPool


class ThreadExecution:

    def test_threading(self):
        nodelist = ["dummy-host%02d" % (i) for i in range(1, 300)]

        target_size = len(nodelist) * 2

        self.data = []
        self.a = {}

        def func(data):
            self.data.append(threading.get_ident())
            import time

            self.a.setdefault(threading.get_ident(),0)
            time.sleep(0.51)
            self.a[threading.get_ident()] = self.a[threading.get_ident()] + 1
            self.data.append(threading.get_ident())

        pool = ThreadPool.ThreadPool(100)

        pool.map(func, nodelist)
        pool.wait_completion()
        assert_equal(len(self.data), target_size)

        sum = 0
        for key, value in self.a.items():
            sum += value
        assert_equal(sum, len(nodelist))




