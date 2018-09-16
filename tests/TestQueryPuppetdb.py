import os
import sys
import configparser
from nose.tools import *
from pprint import pprint
from nose.plugins.attrib import attr

RUNDIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.path.append(RUNDIR + "/lib/")
from catalogtests import Helper

from catalogtests import QueryPuppetdb

class TestQueryPuppetdb:


    def get_config():
        configfile = Helper.Helper.get_config_file()
        config_puppetdb = {}
        try:
            config = configparser.RawConfigParser()
            config.read(configfile)

            config_puppetdb = config._sections['puppetdb']
        except:
            raise Exception("Error reading the configuration file %s" % args.config.name)
        return config_puppetdb

    # TODO: mock the requests

    @nottest
    def test_host_query(self):
        qpdb = QueryPuppetdb.QueryPuppetdb(TestQueryPuppetdb.get_config(), True)
        node_list = qpdb.get_hosts_by_hostnames('barfoo_master', ['foo.bar.baz.net'])
        assert_equal(1, len(node_list))
        assert_true("environment" in node_list[0] and node_list[0]["environment"] == "barfoo_master")
        assert_true("nodename" in node_list[0] and node_list[0]["nodename"] == "foo.bar.baz.net")

    @nottest
    def test_env_query(self):
        qpdb = QueryPuppetdb.QueryPuppetdb(TestQueryPuppetdb.get_config(), True)
        node_list = qpdb.get_hosts_by_environment('barfoo', 'barfoo_master')
        assert_true(len(node_list) > 50)

    @nottest
    def test_get_environments_with_nodes(self):
        qpdb = QueryPuppetdb.QueryPuppetdb(TestQueryPuppetdb.get_config(), True)
        res_all = qpdb.get_environments_with_nodes()
        res_ded = qpdb.get_hosts_by_environment('barfoo', 'barfoo_master')
        assert_true(len(res_all) > 50)
        assert_true(len(res_all['barfoo_master']) == len(res_ded) and len(res_ded) > 10)
