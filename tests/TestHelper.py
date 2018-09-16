import codecs
import os
import sys
import argparse

from nose.tools import *

RUNDIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.path.append(RUNDIR + "/lib/")

from catalogtests import Helper

class TestExecution:


    def test_get_config_file(self):
        res = Helper.Helper.get_config_file()
        print(res)
        assert_true(res is not None)

    def test_get_ownership_details(self):
      (uid, gid) = Helper.Helper.get_ownership_details()
      assert_true(isinstance(uid, int))
      assert_true(isinstance(gid, int))

    def test_set_file_permissions(self):
        file = RUNDIR + "/tests/tmp/foo.txt"
        with codecs.open(file, "w", "utf-8") as fd:
            Helper.Helper.set_file_permissions(file)
            fd.write("BOING")

    def test_process_arguments_no_arguments(self):

        argv = []
        args, additional_info, exitcode, parser = Helper.Helper.process_arguments(argv,
                                                                          Helper.Helper.get_config_file(),
                                                                          disable_exit_on_error=True)
        assert_true("one of the arguments --nodesof --host --all is required" in additional_info)

    def test_process_arguments_broken_arguments(self):
        argv = []
        argv.append("--foobarbaz")
        args, additional_info, exitcode, parser = Helper.Helper.process_arguments(argv,
                                                                          Helper.Helper.get_config_file(),
                                                                          disable_exit_on_error=True)
        assert_true("one of the arguments --nodesof --host --all is required" in additional_info)
        assert_true("unrecognized arguments: --foobarbaz" in additional_info)


    def test_process_arguments_good_arguments(self):
        argv1 = ['--environment', 'foobar_master', '--host', 'foobar.net', '--debug',
                 '--prepare_git_repo_path_src', '/etc/puppet/environments_src', '--prepare_git_repo_path',
                 '/etc/puppet/environments', '--manage_shared_env', 'production']

        args, additional_info, exitcode, parser = Helper.Helper.process_arguments(argv1,
                                                                          Helper.Helper.get_config_file(),
                                                                          disable_exit_on_error=True)

        assert_true(exitcode == None and len(additional_info) == 0 and args.threads == 1)

    def test_process_arguments_good_arguments2(self):
        argv2 = ['--environment', 'foobar_master', '--host', 'foobar.net', '--debug', '--jsondir', '/tmp',
                 '--junitdir', '/tmp/', '--prepare_git_repo_path', '/etc/puppet/environments/', '--manage_shared_env',
                 'production', '--prepare_git_repo_path_src', '/etc/puppet/environments_src']

        args, additional_info, exitcode, parser = Helper.Helper.process_arguments(argv2,
                                                                          Helper.Helper.get_config_file(),
                                                                          disable_exit_on_error=True)

        assert_true(exitcode == None and len(additional_info) == 0 and args.threads == 1)

    def test_process_arguments_good_arguments3(self):
        argv3 = ['--environment', 'foobar_master', '--nodesof', 'foobar_master', '--debug', '--jsondir', '/tmp',
                 '--junitdir',
                 '/tmp/', '--threads', '20', '--prepare_git_repo_path', '/etc/puppet/environments/', '--manage_shared_env',
                 'production', '--prepare_git_repo_path_src', '/etc/puppet/environments_src']

        args, additional_info, exitcode, parser = Helper.Helper.process_arguments(argv3,
                                                                          Helper.Helper.get_config_file(),
                                                                          disable_exit_on_error=True)


        assert_true(exitcode == None and len(additional_info) == 0 and args.threads == 20)

    def test_process_arguments_good_arguments4(self):
        argv4 = ['--all', '".*"', '--debug', '--jsondir', '/tmp', '--junitdir', '/tmp/', '--threads', '20',
                 '--prepare_git_repo_path', '/etc/puppet/environments/', '--manage_shared_env', 'production',
                 '--prepare_git_repo_path_src', '/etc/puppet/environments_src',
                 ]

        args, additional_info, exitcode, parser = Helper.Helper.process_arguments(argv4,
                                                                          Helper.Helper.get_config_file(),
                                                                          disable_exit_on_error=True)
        print(additional_info)
        assert_true(exitcode == None and len(additional_info) == 0 and args.threads == 20)
