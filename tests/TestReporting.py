import os
import sys
from nose.tools import *
from xml.dom import minidom


RUNDIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.path.append(RUNDIR + "/lib/")

from catalogtests import CatalogRun
from catalogtests import Reporting

class TestReporting:

    def test_report(self):
        results = []

        # TODO: too lazy, mock this later
        ex1 = CatalogRun.CatalogRun('barenv', 'foohost1')
        ex1.setNewFormatstring("ls /etc/fstab /etc/bla")
        ex1.execute_catalog_test()
        results.append(ex1)

        ex2 = CatalogRun.CatalogRun('barenv', 'foohost2')
        ex2.setNewFormatstring("ls /etc/fstab")
        ex2.execute_catalog_test()
        results.append(ex2)

        ex3 = CatalogRun.CatalogRun('bar2env', 'foohost2')
        ex3.setNewFormatstring("ls /etc/fstab")
        ex3.execute_catalog_test()
        results.append(ex2)

        rep = Reporting.Reporting(results, True)
        rep.gather_results()

    def test_report_junit(self):
        results = []

        # TODO: too lazy, mock this later
        ex1 = CatalogRun.CatalogRun('barenv', 'foohost1')
        ex1.setNewFormatstring("ls /etc/fstab /etc/bla")
        ex1.execute_catalog_test()
        results.append(ex1)

        rep = Reporting.Reporting(results, True)

        tmpdir = RUNDIR+"/tests/tmp/"
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)

        rep.gather_results(tmpdir)

        xmldoc = minidom.parse(tmpdir + "/barenv.xml")
        assert_true(isinstance(xmldoc, minidom.Document))

