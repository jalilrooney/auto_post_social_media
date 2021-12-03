# -*- coding: utf-8 -*-
import re
import sys
from lxml import html

# to improve performance, regex statements are compiled only once per module
re_newline_spc = re.compile(r'(?<=\n)( )+')
re_starting_whitespc = re.compile(r'^[ \t\n\r\f]*')
re_multi_spc_tab = re.compile(r'[ \t]+(?=([ \t]))')
re_double_newline = re.compile(r'[ \n]+(?=(\n))')
re_ending_spc_newline = re.compile(r'[ \n]*$')


class Cleaner:
    def delete_tags(self, arg):
        if len(arg) > 0:
            try:
                raw = html.fromstring(arg)
            except ValueError:
                raw = html.fromstring(arg.encode("utf-8"))
            return raw.text_content().strip()

        return arg

    def delete_whitespaces(self, arg):
        # Deletes whitespaces after a newline
        arg = re.sub(re_newline_spc, '', arg)
        # Deletes every whitespace, tabulator, newline at the beginning of the string
        arg = re.sub(re_starting_whitespc, '', arg)
        # Deletes whitespace or tabulator if followed by whitespace or tabulator
        arg = re.sub(re_multi_spc_tab, '', arg)
        #  Deletes newline if it is followed by an other one
        arg = re.sub(re_double_newline, '', arg)
        # Deletes newlines and whitespaces at the end of the string
        arg = re.sub(re_ending_spc_newline, '', arg)
        return arg

    def clean(self, arg):
        if arg is not None:
            if isinstance(arg, list):
                newlist = []
                for entry in arg:
                    newlist.append(self.clean(entry))
                return newlist
            else:
                if sys.version_info[0] < 3:
                    arg = unicode(arg)
                else:
                    arg = str(arg)
                arg = self.delete_tags(arg)
                arg = self.delete_whitespaces(arg)
                return arg
        else:
            return None
