import os
import re
from pprint import pprint
import codecs
import shutil
from collections import OrderedDict
from catalogtests import Helper


class CommandlineOutputReporting(object):

    MESSAGETYPES_ORDERED = ['Error', 'Warning', 'Notice']
    TABLE_HEAD = """
<html>
<head>
  <title>Catalogtest Messages</title>
  <script type="text/javascript" src="./jquery-latest.js"></script> 
    <script type="text/javascript" src="./jquery.tablesorter.js"></script>
  <link rel="stylesheet" href="./style.css" type="text/css" media="print, projection, screen" />
  </head>
  <body>
    <h1>%s</h1>
    <p>Overview of all Messages thrown by the catalog-tests.</p>
    <table id="messageTable" class="tablesorter">
        <thead>
            <tr>
                <th width="5%%">Category</th> 
                <th width="5%%">Amount</th>
                <th width="50%%">Message</th>
                <th width="40%%">Nodes</th>
            </tr> 
        </thead>
        <tbody>
"""
    TABLE_FOOTER = """
        </tbody>
    </table>
    <script>
    $(document).ready(function() 
        { 
            $("#messageTable").tablesorter({}); 
        } 
    );
    </script>
    </body>
</html>"""

    def __init__(self, host_objects, debug):
        self.debug = debug
        self.host_objects = host_objects
        self.stats = {}

    def __add_supplementary_files(self, html_filename):

        src_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__))) + "/../../share/html-reports/"
        dst_dir = os.path.realpath(os.path.dirname(os.path.realpath(html_filename)))

        for filename in [ "jquery-latest.js", "jquery.tablesorter.js", "style.css" ]:
            filename_abs = dst_dir+"/"+filename
            shutil.copy(src_dir+"/"+filename,filename_abs)
            Helper.Helper.set_file_permissions(filename_abs)

    def gather_results(self, output="-"):
        ret = -1
        if output == "-":
            ret = self.gather_results_stdout()
        elif output is not None:
            print("\n\nOutput commandline output statistics: %s\n" % output)
            ret = self.gather_results_html(output)
        elif output is None:
            pass
        else:
            raise("No suitable commandline output defined")
        return ret

    def gather_results_stdout(self):
        self.__collect_stats()
        formatstring = "%(category)-10s : %(amount)6s : %(msg)s"

        print("\n**** REPORT:\n")
        print(formatstring % {'category': "Category", 'amount': 'Amount', 'msg': 'Unified message'})
        num = 0
        for category in CommandlineOutputReporting.MESSAGETYPES_ORDERED:
            if category not in self.stats:
                continue
            ordered_dict = OrderedDict(sorted(self.stats[category].items(), key=lambda x: x[1]['count'], reverse=True))
            for msg, data in ordered_dict.items():
                msg = msg.strip()
                amount = data['count']
                print(formatstring % {'category': category, 'amount': amount, 'msg': msg})
                num += 1
        return num

    def gather_results_html(self, filename):
        self.__collect_stats()
        self.__add_supplementary_files(filename)
        formatstring = " " * 12 + "<tr><td>%(category)s</td><td>%(amount)s</td><td>%(msg)s</td><td>%(nodes)s</td></tr>\n"
        report = CommandlineOutputReporting.TABLE_HEAD % "Output Report"

        num = 0
        for category in CommandlineOutputReporting.MESSAGETYPES_ORDERED:
            if category not in self.stats:
                continue

            ordered_dict = OrderedDict(sorted(self.stats[category].items(), key=lambda x: x[1]['count'], reverse=True))
            for msg, data in ordered_dict.items():
                msg = msg.strip()
                amount = data['count']
                nodes = ", ".join(data['nodes'])
                report += formatstring % {'category': category, 'amount': amount, 'msg': msg, 'nodes': nodes}
                num += 1

        report += CommandlineOutputReporting.TABLE_FOOTER

        if self.debug:
            print(report)

        with codecs.open(filename, "w", "utf-8") as html_fd:
            helper = Helper.Helper.set_file_permissions(filename)
            html_fd.write(report)
        return num

    @staticmethod
    def unify_message(msg):
        # Scope(Haproxy::Frontend[XXXX])
        msg = re.sub(r"(.*)Scope\((.+)\[(.+)\]\)", r"\1Scope(\2[UNIFIED])", msg)
        msg = re.sub(r"Failed to execute '/pdb/cmd/v1.*", r"Failed to execute '/pdb/cmd/v1[UNIFIED]", msg)
        msg = re.sub(r"Compiled catalog for .* in environment .* in \d+.\d+ seconds",
                     r"Compiled catalog for [UNIFIED] in environment [UNIFIED] in [UNIFIED] seconds", msg)

        msg = re.sub(r"on node ([a-zA-Z0-9\.\-]*\.[^\s]{2,}\.?)",
                     r"on node [UNIFIED]", msg)

        return msg

    def __collect_stats(self):
        def __collect_stats_stream(stream, hostname):
            regex_partial = "|".join(CommandlineOutputReporting.MESSAGETYPES_ORDERED)
            for line in stream.splitlines():
                line = CommandlineOutputReporting.unify_message(line)
                m = re.match('.*(%s):(.*)' % regex_partial, line)
                if m:
                    type = m.group(1)
                    message = m.group(2)
                    self.stats.setdefault(type, {})
                    self.stats[type].setdefault(message, {})
                    self.stats[type][message].setdefault('nodes', [])
                    self.stats[type][message].setdefault('count', 0)
                    self.stats[type][message]['count'] += 1
                    self.stats[type][message]['nodes'].append(hostname)

        for host_obj in self.host_objects:
            __collect_stats_stream(host_obj.getStdout(), host_obj.getHostname())
            __collect_stats_stream(host_obj.getStderr(), host_obj.getHostname())
