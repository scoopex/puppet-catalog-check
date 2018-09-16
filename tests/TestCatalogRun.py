import os
import sys
import nose

import logging
from pprint import pprint
from nose.tools import *

RUNDIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.path.append(RUNDIR + "/lib/")

from catalogtests import CatalogRun

class TestExecution:

    def test_instance(self):
        ex = CatalogRun.CatalogRun('foo', 'foohost')
        assert_true(isinstance(ex, CatalogRun.CatalogRun))

    def test_formatstring(self):
        ex = CatalogRun.CatalogRun('fooenv', 'foohost')
        thrown = False
        try:
            ex.setNewFormatstring("false %(boing)")
        except KeyError:
            thrown = True
        assert_true(thrown)

    def test_exitcode(self):
        ex = CatalogRun.CatalogRun('fooenv', 'foohost')
        ex.setNewFormatstring("ls /etc/fstab /etc/bla")
        ex.execute_catalog_test()
        assert_equal(2, ex.getExitcode())


    def test_time(self):
        ex = CatalogRun.CatalogRun('foo', 'foohost')
        ex.setNewFormatstring("sleep 0.01")
        ex.execute_catalog_test()
        assert_true(ex.getTime() > 0)

    def test_json_extraction(self, file_name=None):
        string_with_json = """PREFIX TEXT....}
            {"one" : {"one" : "1", "two" : "2", "three" : "3"}
            , "two" : "2", "three" : "3"}
            ....{POSTFIX TEXT"""

        (remaining, json_dict, json_file) = CatalogRun.CatalogRun.process_json(string_with_json, json_file=file_name)
        print("REMAINING: >>>%s<<<" % remaining)
        print("JSON: >>>%s<<<" % json_dict)

        assert_true(type(json_dict) == dict)
        assert_equal(remaining.index("PREFIX TEXT...."), 0)
        assert_equal(remaining.index("...{POSTFIX TEXT"), 66)
        assert_equal(remaining.index("[[JSON REMOVED HERE]]"), 30)

    def test_json_extraction_with_json(self):
        tmpdir = RUNDIR + "/tests/tmp/"
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        self.test_json_extraction(tmpdir+"/testfile.json")
        


