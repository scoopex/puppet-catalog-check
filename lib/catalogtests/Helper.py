import os
import argparse



class Helper(object):

    debug = False
    permission_reference_dir = __file__
    configfile = None

    @staticmethod
    def get_config_file():
        libdir = os.path.dirname(os.path.realpath(__file__))
        projectdir = os.path.realpath(libdir + "/../../")
        possible_files = []
        possible_files.append("/supplementary/config/catalog_test.config")
        possible_files.append(projectdir + "/../supplementary/config/catalog_test.config")
        possible_files.append(projectdir + "/etc/catalog_test.config")
        for filename in possible_files:
            if os.path.exists(filename):
                filename = os.path.realpath(filename)
                return filename
        return None

    @staticmethod
    def set_file_permissions(file):
        (uid, gid) = Helper.get_ownership_details()
        os.chown(file, uid, gid)
        os.chmod(file, 0o644)

    @staticmethod
    def get_ownership_details(dir=permission_reference_dir):

        if not os.path.exists(dir):
            raise Exception("reference dir %s does not exist" % dir)
        stat_info = os.stat(dir)
        return (stat_info.st_uid, stat_info.st_gid)

    @staticmethod
    def process_arguments(argv, default_config, disable_exit_on_error = False):

        exitcode = None
        additional_info = []

        def bypass_error(message):
            print("ERROR OUTPUT RAISED: >>>" + message +  "<<<")
            additional_info.append(message)

        parser = argparse.ArgumentParser(
            description='perform catalog compiles/tests using real puppetdb facts',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            epilog="""
        """
        )

        # Override argparse.ArgumentParser.error(self, message)
        if disable_exit_on_error:
            parser.error = bypass_error

        ########################################################################################################################
        ## Global options
        args_global = parser.add_argument_group('Global options')
        args_global.add_argument(
            '--debug',
            help='Output debug information',
            action='store_true',
        )
        args_global.add_argument(
            '--problem_output',
            help='Output problem information',
            action='store_true',
        )
        args_global.add_argument(
            '--config',
            nargs='?',
            type=argparse.FileType('r'),
            help='configuration file',
            default=default_config,
            required=False,
        )
        ########################################################################################################################
        # parameters of the catalog compiles
        args_global.add_argument(
            '--threads',
            nargs='?',
            type=int,
            help='Execute the catalog tests in a defined number of threads to reduce execution time',
            default=1,
            required=False,
        )
        args_global.add_argument(
            '--certname',
            nargs='?',
            help='The name of the puppet client cert which is used to interact with puppetdb',
            type=str,
            required=False,
            default='foo.bar.baz.net',
        )
        ########################################################################################################################
        ## What to process
        args_processing = parser.add_argument_group('What to process')
        args_processing.add_argument(
            '--environment',
            nargs='?',
            type=str,
            help='The name of the environment to execute the catalogtests in',
            default=None,
        )
        parser_group = args_processing.add_mutually_exclusive_group(required=True)
        parser_group.add_argument(
            '--nodesof',
            nargs='?',
            help='The name of the environment to to get the hostnames from',
            default=None,
        )
        parser_group.add_argument(
            '--host',
            nargs='*',
            help='The names of one ore more hostnames',
            default=None,
            action='append',
        )
        parser_group.add_argument(
            '--all',
            nargs='?',
            help='Execute on all known environments, add a regex to filter environments',
            type=str,
        )
        ########################################################################################################################
        # output/result parameters
        args_output = parser.add_argument_group('Output/result parameters')
        args_output.add_argument(
            '--jsondir',
            nargs='?',
            type=str,
            help='The name of the directory to dump compiled catalogs in json format ' +
                 '(useful if you want to run statistics of differential analysis)',
            required=False,
        )
        args_output.add_argument(
            '--junitdir',
            nargs='?',
            type=str,
            help='Output junit data to this directory. (useful if you like to process the results ' +
                 'in a automated way, i.e. in jenkins)',
            required=False,
        )
        args_output.add_argument(
            '--puppet_output_stats',
            nargs='?',
            type=str,
            help='Output statistics, "-" for stdout, a filename for html',
            required=False,
            default=None,
        )
        args_output.add_argument(
            '--fail_percentage',
            nargs='?',
            type=int,
            help='Specifies the maximum percentage of failed hosts, on which the build is considered to be broken',
            default=20,
            required=False,
        )
        ########################################################################################################################
        # branch and environment management
        args_environments = parser.add_argument_group('Environment parameters, manage git checkouts')
        args_environments.add_argument(
            '--prepare_git_repo_path',
            nargs='?',
            help='The path of the puppet environment dir where git checkouts should be managed.' +
                 'On specification the branch names are append based on the branch information in puppetdb',
            type=str,
            required=False,
            default=None,
        )
        args_environments.add_argument(
            '--prepare_git_repo_path_src',
            nargs='?',
            help='The path of the directory where the base repo checkouts are located for the option --prepare_git_repo_path,' +
                 'this defaults to the value specified by "--prepare_git_repo_path". ' +
                 '',
            type=str,
            required=False,
            default=None,
        )
        args_environments.add_argument(
            '--manage_shared_env',
            nargs='?',
            help='Specify the name of the central shared environment, appending the branch ' +
                 'prefix will be suppressed for this repo',
            required=False,
            type=str,
            default=None,
        )
        args_environments.add_argument(
            '--override_branches',
            nargs='?',
            help='Override all branches by the specified branch (useful for development)',
            required=False,
            type=str,
            default=None,
        )
        args_environments.add_argument(
            '--purge_existing_envs',
            help='Purge existing branch environments',
            action='store_true',
        )

        args = parser.parse_args(argv)

        if args.manage_shared_env and args.prepare_git_repo_path_src is None:
            parser.error("--manage_shared_env requires --prepare_git_repo_path_src")
            exitcode = 1
        if args.override_branches and args.prepare_git_repo_path_src is None:
            parser.error("--override_branches requires --prepare_git_repo_path_src")
            exitcode = 1
        if args.nodesof == 'same':
            args.nodesof = args.environment
        if args.threads < 1:
            parser.error("ERROR: specify a number > 0")
            exitcode = 1
        if args.jsondir != None and not os.path.isdir(args.jsondir):
            parser.error("ERROR: path for json files '%s' does not exist\n" % args.jsondir)
            exitcode = 1

        return (args, additional_info, exitcode, parser)
