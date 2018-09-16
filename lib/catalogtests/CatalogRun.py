import json
import re
import time
import subprocess
import sys
import codecs
from catalogtests import Helper

from pprint import pprint

RE_OUTPUT_PARSE = re.compile(r"^(?P<preJson>.*?)(?P<json>{.+})(?P<postJson>.*)$", re.DOTALL)

class CatalogRun(object):

    def __init__(self, environment, host, debug=False):
        self.env = environment
        self.host = host
        self.debug = debug
        self.output_problems = False
        self.cmd_formatstring = "puppet master --color false --logdest console --compile %(host)s " +\
                                "--environment %(environment)s --certname %(certname)s"
        self.result = {"host": host}
        self.cmd = None
        self.certname = None
        self.json_dump_file = None

    def setNewFormatstring(self, cmd_formatstring):
        test = cmd_formatstring % {'host:': self.host, 'environment': self.env, 'certname': self.certname}
        self.cmd_formatstring = cmd_formatstring
        sys.stdout.write("Set new formatstring: >>>%s<<<\n" % self.cmd_formatstring)

    def problem_output(self, what):
        self.output_problems = what

    def set_certname(self, what):
        self.certname = what

    def set_json_dump_dir(self, dir):
        if dir is None:
            self.json_dump_file = None
        else:
            self.json_dump_file = "%s/%s_%s.json" % (dir, self.env, self.host)

    @staticmethod
    def process_json(string, json_file=None, json_replacement='\n[[JSON REMOVED HERE]]\n', debug=False):
        if json_file is not None:
            json_file = re.sub("/+", "/", json_file)

        m = RE_OUTPUT_PARSE.match(string)
        if m:
            if json_file is not None:
                if debug:
                    sys.stderr.write("INFO: extracting json and saving to '%s'\n" % json_file)
                with codecs.open(json_file, "w", "utf-8") as jsonfd:
                    Helper.Helper.set_file_permissions(json_file)
                    jsonfd.write(m.group("json"))

            remaining = m.group("preJson") + json_replacement + m.group("postJson")
            json_dict = json.loads(m.group("json"))
        else:
            remaining = string
            json_dict = None

        return (remaining, json_dict, json_file)

    @staticmethod
    def output_errors_and_warnings(output):
        for line in output.splitlines():
            if re.match('^(Warning|Error):', line):
                print(line)

    def execute_catalog_test(self):
        sys.stdout.write("===> STARTING '%s' for environment '%s'\n" % (self.host, self.env))
        cmd = self.cmd_formatstring % {'host': self.host, 'environment': self.env, 'certname': self.certname}

        if self.debug:
            sys.stderr.write("EXEC: %s\n" % cmd)

        start = time.time()

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (stdout, stderr) = process.communicate()
        end = time.time()
        self.result['stderr'] = stderr.decode('utf8')

        (self.result['stdout'], self.result['json_catalog'], self.result['json_file']) = \
            CatalogRun.process_json(stdout.decode('utf8'), json_file=self.json_dump_file, debug=self.debug)
        self.result['cmd'] = cmd
        self.result['exitcode'] = process.returncode
        self.result['environment'] = self.env
        self.result['time'] = end - start

        if self.debug:
            sys.stderr.write("STDOUT >>>%s<<<\n" % self.result['stdout'])
            sys.stderr.write("STDERR >>>%s<<<\n" % self.result['stderr'])
        elif self.output_problems:
            CatalogRun.output_errors_and_warnings(self.result['stderr'])

        sys.stdout.write(
            "===> COMPLETED '%(host)s' for environment '%(environment)s' , exitcode %(exitcode)d, %(time).4f seconds\n" % self.result)

    def getEnvironment(self):
        return self.env

    def getHostname(self):
        return self.host

    def getStdout(self):
        return self.result['stdout']

    def getStderr(self):
        return self.result['stderr']

    def getExitcode(self):
        return self.result['exitcode']

    def getEnv(self):
        return self.result['environment']

    def getTime(self):
        return self.result['time']

    def getCommand(self):
        return self.result['cmd']

    def hasCatalog(self):
        if self.result['json_catalog'] is not None:
            return True
        else:
            return False
