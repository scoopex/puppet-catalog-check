import re
import subprocess
import sys
import codecs
import os
from catalogtests.threads import ThreadPool
from catalogtests import Helper

from pprint import pprint


class ManageGitCheckout(object):

    def __init__(self, src, dst, branch, debug, purge_existing_environments):
        self.src = src
        self.dst = dst
        self.branch = branch
        self.debug = debug
        self.purge_existing_environments = purge_existing_environments

        if not os.path.isabs(src):
            raise Exception("%s is not absolute path" % src)
        if not os.path.isabs(dst):
            raise Exception("%s is not absolute path" % dst)
        if branch is None:
            raise Exception("no branch specified")

        if self.debug:
            sys.stderr.write("DEBUG: %s => %s and branch %s\n" % (self.src, self.dst, branch))

    def __execute_command(self, cmd, prev_ret, workingdir=None):

        if prev_ret is False:
            return prev_ret

        if self.debug:
            out = "EXEC: %s" % cmd
            if workingdir is not None:
                out += " with workingdir %s" % workingdir
            sys.stderr.write(out + "\n")

        if workingdir is None:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        else:
            process = subprocess.Popen(cmd, cwd=workingdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        out, err = process.communicate()

        if process.returncode != 0:
            success = False
        else:
            success = True

        if self.debug or (success is False):
            if out.decode('utf8') is not "":
                sys.stderr.write("STDOUT: >>>%s<<<\n" % out.decode('utf8'))
            if err.decode('utf8') is not "":
                sys.stderr.write("STDERR: >>>%s<<<\n" % err.decode('utf8'))

        if process.returncode != 0:
            raise Exception("FAILED: %s\n" % cmd)

        return success

    def gather_numeric_ownership(self, dir):
        uid = 0
        gid = 0

        return (uid, gid)

    def manage_git_env(self):
        prev_ret = True

        if not self.purge_existing_environments and os.path.exists(self.dst):
            if self.debug:
                sys.stderr.write("INFO: skipping prepare for %s/%s\n" % (self.src, self.dst))
            return prev_ret

        if os.path.exists(self.dst):
            prev_ret = self.__execute_command("rm -rf %s" % self.dst, prev_ret)
        prev_ret = self.__execute_command("cp -a %s %s" % (self.src, self.dst), prev_ret)
        prev_ret = self.__execute_command("git -C %s checkout %s" % (self.dst, self.branch), prev_ret)
        prev_ret = self.__execute_command("r10k puppetfile install", prev_ret, workingdir=self.dst)

        uid, gid = Helper.Helper.get_ownership_details()
        prev_ret = self.__execute_command("chown -R %s:%s %s" % (uid, gid, self.dst), prev_ret)

        return prev_ret
