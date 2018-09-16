import os
import sys
from nose.tools import *
import random


RUNDIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.path.append(RUNDIR + "/lib/")
from pprint import pprint
from catalogtests import CatalogRun
from catalogtests import CommandlineOutputReporting


class TestCommandlineOutputReporting:
    def test_unify_message(self):
        res = CommandlineOutputReporting.CommandlineOutputReporting.unify_message(
            'Scope(Haproxy::Frontend[alala_lolo]): The $bind_options parameter is deprecated; please use $bind instead')
        assert_equal(res,
                     'Scope(Haproxy::Frontend[UNIFIED]): The $bind_options parameter is deprecated; please use $bind instead')

        res = CommandlineOutputReporting.CommandlineOutputReporting.unify_message(
            "Failed to execute '/pdb/cmd/v1?checksum=abd6215ebcff6b7867f1fbbe7923035fd52d8404&version=9&certname='+"
            "'baz-bar.cloud-foo.net&command=replace_catalog&producer-timestamp=1508514495' on at least 1 of the '+"
            "'following 'server_urls': https://fo.bar.baz.de:8081")
        assert_equal(res, "Failed to execute '/pdb/cmd/v1[UNIFIED]")

        res = CommandlineOutputReporting.CommandlineOutputReporting.unify_message(
            "Notice: Compiled catalog for foo.bar.net in environment boingboing in 66.53 seconds")
        assert_equal(res, "Notice: Compiled catalog for [UNIFIED] in environment [UNIFIED] in [UNIFIED] seconds")

        res = CommandlineOutputReporting.CommandlineOutputReporting.unify_message(
            "Failed to execute on node foo.bar.baz.net ?")
        assert_equal(res, "Failed to execute on node [UNIFIED] ?")
        res = CommandlineOutputReporting.CommandlineOutputReporting.unify_message(
            "Failed to execute on node foo.bar.baz.net")
        assert_equal(res, "Failed to execute on node [UNIFIED]")

    def test_gather_results_stdout(self):
        results = self.__create_testdata()
        rep = CommandlineOutputReporting.CommandlineOutputReporting(results, True)
        assert_equal(rep.gather_results(), 4)

    def test_gather_results_html(self):
        results = self.__create_testdata()
        tmpdir = RUNDIR + "/tests/tmp/"
        rep = CommandlineOutputReporting.CommandlineOutputReporting(results, True)
        assert_equal(rep.gather_results(tmpdir + "/report.html"), 4)


    def __create_testdata(self):
        results = []

        def __fake_fin(host):
            duration = random.uniform(1.5, 211.9)
            return "Notice: Compiled catalog for %s in environment [UNIFIED] in %.2f seconds" % (host, duration)

        # TODO: too lazy, mock this later
        ex1 = CatalogRun.CatalogRun('barenv', 'foohost1.bar.net', debug=True)
        ex2 = CatalogRun.CatalogRun('barenv', 'foohost2.bar.net', debug=True)
        ex3 = CatalogRun.CatalogRun('bar2env', 'foohost2.bar.net', debug=True)


        # 5 Messages, but 3 unique Messages => so we should get a report of 3 Messages
        ex1.setNewFormatstring("/bin/echo -e 'Warning: This was a warning\\nNotice: This was a notice\\n%s\\n'" %
                               __fake_fin(ex1.getHostname()))
        ex2.setNewFormatstring("/bin/echo -e 'Error: This was a error\\n%s\\n'" %
                               __fake_fin(ex2.getHostname()))
        ex3.setNewFormatstring("/bin/echo -e 'Error: This was a error\\nWarning: This was a warning\\n%s\\n'" %
                               __fake_fin(ex3.getHostname()))

        ex1.execute_catalog_test()
        ex2.execute_catalog_test()
        ex3.execute_catalog_test()

        results.append(ex1)
        results.append(ex2)
        results.append(ex2)
        return results

