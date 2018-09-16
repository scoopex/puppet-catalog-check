import os
import sys
import configparser
from nose.tools import *
from pprint import pprint
from nose.plugins.attrib import attr
import shutil

RUNDIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.path.append(RUNDIR + "/lib/")
TMPDIR = RUNDIR+"/tests/tmp/"


from catalogtests import ManageGitCheckouts

class TestManageGitCheckouts:

    def test_check_collisions(self):

        nodelist = [{'environment': 'foobarbaz_preview',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-previewmdb1.boing.net'},
         {'environment': 'foobarbaz_preview',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-preview2.boing.net'},
         {'environment': 'foobarbaz_devel',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-dev4.boing.net'},
         {'environment': 'foobarbaz_devel',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-dev3.boing.net'},
         {'environment': 'foobarbaz_devel',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-dev2.boing.net'},
         {'environment': 'foobarbaz_master',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-fe2.boing.net'},
        ]
        # the good path
        git_mgmt = ManageGitCheckouts.ManageGitCheckouts(nodelist, 3, TMPDIR, TMPDIR, debug=True)
        assert_true(git_mgmt.check_collisions())

        nodelist.append({'environment': 'foobarbaz_master',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-fe2.boing.net'})

        # the bad path
        git_mgmt = ManageGitCheckouts.ManageGitCheckouts(nodelist, 3, TMPDIR, TMPDIR, debug=True)
        assert_false(git_mgmt.check_collisions())

    @staticmethod
    def __exec(cmd):
        print("+%s" % cmd)
        ret = os.system(cmd)
        if ret != 0:
            print("FAILED ECECUTION")

    @staticmethod
    def __create_fake_repo(dir):

        os.mkdir(dir)
        os.chdir(dir)
        os.system("git init .")
        os.system("git config user.email 'you@example.com'")
        os.system("git config user.name 'Your Name'")
        with open("Puppetfile", 'w') as f:
            f.write('forge "https://forgeapi.puppetlabs.com"\n')
            f.write('\n')
            #f.write("mod 'puppetlabs-stdlib'")
        TestManageGitCheckouts.__exec("git add Puppetfile")

        for i in range(1, 20):
            with open(str(i)+".txt", 'w') as f:
                for j in range(i, 0):
                    f.write(("X" * i) + "\n")
            TestManageGitCheckouts.__exec("git add %s.txt" % i)
        TestManageGitCheckouts.__exec("git commit -m 'FOO' -a")
        TestManageGitCheckouts.__exec("git checkout -b devel")
        for i in range(1, 20):
            with open(str(i)+"-2.txt", 'w') as f:
                for j in range(i, 0):
                    f.write(("X" * i) + "\n")
            TestManageGitCheckouts.__exec("git add %s-2.txt" % i)
        TestManageGitCheckouts.__exec("git commit -m 'FOO' -a")
        TestManageGitCheckouts.__exec("git checkout -b preview")
        for i in range(1, 20):
            with open(str(i)+"-3.txt", 'w') as f:
                for j in range(i, 0):
                    f.write(("X" * i) + "\n")
            TestManageGitCheckouts.__exec("git add %s-3.txt" % i)
        TestManageGitCheckouts.__exec("git commit -m 'FOO' -a")


    def test_check_prepare_envs(self):
        TMPDIR_SRC = TMPDIR + "/srcrepos"
        TMPDIR_DST = TMPDIR + "/dstrepos"

        if os.path.isdir(TMPDIR_SRC):
            shutil.rmtree(TMPDIR_SRC)
        if os.path.isdir(TMPDIR_DST):
            shutil.rmtree(TMPDIR_DST)
        os.mkdir(TMPDIR_SRC)
        os.mkdir(TMPDIR_DST)

        TestManageGitCheckouts.__create_fake_repo(TMPDIR_SRC + "/foobarbaz")
        return
        TestManageGitCheckouts.__create_fake_repo(TMPDIR_SRC + "/production")


        nodelist = [{'environment': 'foobarbaz_preview',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-previewmdb1.boing.net'},
         {'environment': 'foobarbaz_devel',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-dev4.boing.net'},
         {'environment': 'foobarbaz_master',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-fe2.boing.net'},
        ]
        # the good path
        git_mgmt = ManageGitCheckouts.ManageGitCheckouts(nodelist, 3, TMPDIR_SRC, TMPDIR_DST,  debug=True)
        assert_true(git_mgmt.check_collisions())
        assert_true(git_mgmt.prepare_envs(manage_shared_env="production"))

        nodelist.append({'environment': 'foobarbaz_break',
          'environment_src': 'foobarbaz',
          'nodename': 'foobarbaz-fe2.boing.net'})
        git_mgmt = ManageGitCheckouts.ManageGitCheckouts(nodelist, 3, TMPDIR_SRC, TMPDIR_DST, debug=True)
        assert_raises(Exception, git_mgmt.prepare_envs("production"))
