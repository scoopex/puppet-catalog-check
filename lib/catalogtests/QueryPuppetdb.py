
from pypuppetdb import connect
from pprint import pprint
import re

class QueryPuppetdb(object):

    def __init__(self, config, debug):
        self.debug = debug
        self.config = config
        self.puppetdb = connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', '8080'),
            ssl_verify=config.get('ssl_verify', False),
            ssl_key=config.get('ssl_key', None),
            ssl_cert=config.get('ssl_cert', None),
        )

    def get_hosts_by_hostnames(self, puppet_src_environment, hosts):
        hosts = QueryPuppetdb._flatten_array_of_arrays(hosts)
        node_list = []
        for nodename in hosts:
            node = self.puppetdb.node(nodename)
            node_list.append(
                {
                 "nodename": node.name,
                 "environment": node.facts_environment,
                 "environment_src": puppet_src_environment,
                 })
        return node_list

    def get_hosts_by_environment(self, puppet_src_environment, nodes_of):
        node_list = []
        nodes = self.puppetdb.nodes(query='["=","catalog_environment","%s"]' % nodes_of)
        for node in nodes:
            node_list.append(
                {"nodename": node.name,
                 "environment": node.facts_environment,
                 "environment_src": puppet_src_environment,
                })
        return node_list

    def get_environments_with_nodes(self, regex_filter=".*"):
        result = {}
        envs = self.puppetdb.environments()
        for env in envs:
            env_name = env["name"]
            if not re.match(regex_filter, env_name):
                if self.debug:
                    print("INFO: filtered out environment '%s'" % env_name)
                continue
            m = re.match(r'^(.*)_(.+)+$', env_name)
            if not m:
                print("WARNING: ignoring environment '%s', does not match" % env_name)
                continue
            puppet_src_env = m.group(1)
            result[env["name"]] = self.get_hosts_by_environment(puppet_src_env, env["name"])
        return result

    @staticmethod
    def _flatten_array_of_arrays(list_of_list):
        return QueryPuppetdb._flatten_array_of_arrays(list_of_list[0]) + (
            QueryPuppetdb._flatten_array_of_arrays(list_of_list[1:]) if len(list_of_list) > 1 else []) if type(
            list_of_list) is list else [list_of_list]
