import re
import sys

from catalogtests.threads import ThreadPool
from catalogtests import ManageGitCheckout

from pprint import pprint


class ManageGitCheckouts(object):

    def __init__(self, envs, threads, basedir, targetdir, debug=False):
        self.debug = debug
        self.envs = envs
        self.threads = threads
        self.basedir = basedir
        if targetdir is None:
            targetdir = basedir
        self.targetdir = targetdir

    def check_collisions(self):
        hosts = {}

        for exec_item in self.envs:
            hosts.setdefault(exec_item['nodename'], 0)
            hosts[exec_item['nodename']] += 1

        collision_list = [j for i, j in hosts.items() if j > 1]

        if len(collision_list) > 0:
            for name in collision_list:
                sys.stderr.write("ERROR: collision for '%s'\n" % name)
            return False
        else:
            return True

    @staticmethod
    def __replace_double_slash(path):
        path = re.sub(r"/+", r"/", path)
        return path

    def prepare_envs(self, branch=None, manage_shared_env=None, purge_existing_environments=True):

        env_mappings = {}

        for item in self.envs:
            target_env = item["environment"]

            m = re.match("(.+)_(.+)", target_env)
            if not m:
                sys.stderr.write("ERROR: unable to parse branch '%s'\n" % target_env)
                return False
            base_env_dir = m.group(1)
            l_branch = m.group(2)

            if branch is not None:
                l_branch = branch

            src_env_dir = ManageGitCheckouts.__replace_double_slash(self.basedir + "/" + base_env_dir)
            dst_env_dir = ManageGitCheckouts.__replace_double_slash(self.targetdir + "/" + target_env)

            if item["environment"] not in env_mappings:
                env_mappings.setdefault(item["environment"], {})
                env_mappings[item["environment"]] = \
                    ManageGitCheckout.ManageGitCheckout(src_env_dir, dst_env_dir, l_branch, self.debug,
                                                        purge_existing_environments)

        # Prepare shared production folder
        if manage_shared_env is not None:
            env_mappings = self.queue_shared_environment(branch, env_mappings, manage_shared_env,
                                                         purge_existing_environments)

        prepare_env_objects = env_mappings.values()

        self.process_prepare_envs(prepare_env_objects)

        return True

    def process_prepare_envs(self, prepare_env_objects):
        def thread_func_prepare_envs(ex):
            ex = ex.manage_git_env()

        # execute the prepares in parallel
        if self.debug:
            sys.stderr.write("DEBUG: have to git-prepare %i environments\n" % len(prepare_env_objects))
        if self.threads == 1:
            for env_to_prepare in prepare_env_objects:
                thread_func_prepare_envs(env_to_prepare)
        else:
            pool = ThreadPool.ThreadPool(self.threads)
            pool.map(thread_func_prepare_envs, prepare_env_objects)
            pool.wait_completion()

    def queue_shared_environment(self, branch, env_mappings, manage_shared_env, purge_existing_environments):
        src_env_dir = ManageGitCheckouts.__replace_double_slash(self.basedir + "/" + manage_shared_env)
        dst_env_dir = ManageGitCheckouts.__replace_double_slash(self.targetdir + "/" + manage_shared_env)
        if branch is None:
            branch = "production"
        env_mappings[manage_shared_env] = \
            ManageGitCheckout.ManageGitCheckout(src_env_dir, dst_env_dir, branch, self.debug,
                                                purge_existing_environments)

        return env_mappings
