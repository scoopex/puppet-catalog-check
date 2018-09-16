
from threading import Thread
from threading import Lock
import traceback
import sys

class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                # An exception happened in this thread
                print("Exception happened:")
                print('-' * 60)
                sys.stderr.write(str(e))
                sys.stderr.write("\n")
                traceback.print_exc(file=sys.stderr)
                print('-' * 60)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()
