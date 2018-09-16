import datetime
import sys
import re
from pprint import pprint
import codecs
import traceback
from catalogtests import Helper

# DISCLAIMER:
# Das ist das Reports Code Spaghetti Monster, das ist nicht schön da der Code schwer zu überschauen ist.
# Wenn Zeit ist sollten die verschiedenen Report Typen in dedizierte
# Klassen aufgeteilt werden die von einem Interface erben (Factory Pattern).

# to lazy to use a xml lib :-)
""" MAIN
<?xml version="1.0" encoding="UTF-8"?>
<testsuites disabled="" errors="" failures="" name="" tests="" time="">
    <testsuite disabled="" errors="" failures="" hostname="" id="" name="" package="" skipped="" tests="" time="" timestamp="">
...
    </testsuite>
</testsuites>
"""

FILE_SKELETON_MAIN = """<?xml version="1.0" encoding="UTF-8" ?>
<testsuites disabled="0" errors="%(errors)i" failures="%(failures)i" name="ENVIRONMENT: %(environment)s" tests="%(tests)i" time="%(time).4f">
  <testsuite errors="%(errors)i" failures="%(failures)i" name="ENVIRONMENT: %(environment)s" tests="%(tests)i" time="%(time).4f" timestamp="%(timestamp_testexecution)s">
%(output)s
  </testsuite>
</testsuites>
"""

""" TESTCASE
        <properties>
            <property name="" value=""/>
        </properties>
        <testcase assertions="" classname="" name="" status="" time="">
            <skipped/>
            <error message="" type=""/>
            <failure message="" type=""/>
            <system-out/>
            <system-err/>
        </testcase>
        <system-out/></system-out>
        <system-err/></system-err>
    </testsuite>
"""

TESTCASE_SKELETON_TEST_SUCCESS = """
    <testcase classname="%(environment)s" name="%(hostname)s" time="%(time).4f"><system-out><![CDATA[
CMD:
%(cmd)s    

STDOUT:
%(stdout)s
STDERR:
%(stderr)s

]]></system-out>
   </testcase>
        """

TESTCASE_SKELETON_TEST_ERROR = """
    <testcase classname="%(environment)s" name="%(hostname)s" time="%(time).4f">
       <failure type="BrokenCatalog"><![CDATA[
CMD:
%(cmd)s

STDOUT:
%(stdout)s
STDERR:
%(stderr)s
]]>
       </failure>
    </testcase>
        """


class Reporting(object):
    def __init__(self, host_objects, debug):
        self.debug = debug
        self.host_objects = host_objects

    def gather_results(self, junitdir=None, warnings_overview=None):
        testresults = {}
        testresults = self.gather_results_host(testresults)
        return self.gather_results_environments(junitdir, testresults)

    def gather_results_host(self, testresults):
        for result_host in self.host_objects:

            testresults.setdefault(result_host.getEnvironment(),
                                   {"total_time": 0.0, "output": "", "failed": 0, "successful": 0, "output": ""})
            testresults[result_host.getEnvironment()]["total_time"] += result_host.getTime()

            result = {}
            result['hostname'] = result_host.getHostname()
            result["time"] = result_host.getTime()
            result['stdout'] = result_host.getStdout()
            result['stderr'] = result_host.getStderr()
            result['environment'] = result_host.getEnvironment()
            result['cmd'] = result_host.getCommand()

            if result_host.hasCatalog():
                testresults[result_host.getEnvironment()]["successful"] += 1
                sys.stdout.write(self.get_hostresult_formatstring() % (result_host.getHostname(), "SUCCESSFUL"))
                testresults[result_host.getEnvironment()]['output'] += TESTCASE_SKELETON_TEST_SUCCESS % result
            else:
                testresults[result_host.getEnvironment()]["failed"] += 1
                sys.stderr.write(self.get_hostresult_formatstring() % (result_host.getHostname(), "FAILED"))
                testresults[result_host.getEnvironment()]['output'] += TESTCASE_SKELETON_TEST_ERROR % result
        return testresults

    def get_hostresult_formatstring(self):
        hostname_textlength = 0
        for result_host in self.host_objects:
            if hostname_textlength < len(result_host.getHostname()):
                hostname_textlength = len(result_host.getHostname())
        formatstring_hostresult = "%-" + str(hostname_textlength + 1) + "s %s\n"
        return formatstring_hostresult

    def gather_results_environments(self, junit_dir, testresults):
        timestamp_testexecution = datetime.datetime.now().isoformat()

        failed_hosts = 0
        num_envs = 0
        for env, result in testresults.items():
            num_envs += 1
            sys.stderr.write("\n\n")
            f_template = "%35s %s\n"
            self.write_junit_file(env, f_template, junit_dir, result, timestamp_testexecution)

            host_count = result['failed'] + result['successful']
            sys.stderr.write(f_template % ("Environment", env))
            sys.stderr.write(f_template % ("Total Hosts", host_count))
            sys.stderr.write(f_template % ("Failed Hosts", result['failed']))
            failed_hosts += result['failed']
            sys.stderr.write(f_template % ("Successful Hosts", result['successful']))

        return (num_envs, failed_hosts)

    def write_junit_file(self, env, f_template, junit_dir, result, timestamp_testexecution):
        if junit_dir is not None:
            junit_filename = re.sub("/+", "/", ("%s/%s.xml" % (junit_dir, env)))
            with codecs.open(junit_filename, "w", "utf-8") as junit_fd:
                helper = Helper.Helper.set_file_permissions(junit_filename)
                try:
                    junit_fd.write(FILE_SKELETON_MAIN % {
                        'errors': result['failed'],
                        'failures': result['failed'],
                        'environment': env,
                        'tests': result['failed'] + result['failed'],
                        'time': result['total_time'],
                        'timestamp_testexecution': timestamp_testexecution,
                        'output': result['output']
                    }
                                   )
                except Exception as e:
                    # An exception happened in this thread
                    print
                    "Exception happened:"
                    print
                    '-' * 60
                    sys.stderr.write(e)
                    sys.stderr.write("\n")
                    traceback.print_exc(file=sys.stderr)
                    print
                    '-' * 60

                sys.stderr.write(f_template % ("Output file", junit_filename))
