import sys
#import parsedb
import dps_parse_db as parsedb
import tableformatter as tf

import pprint
pp = pprint.PrettyPrinter(indent=4, stream=sys.stderr)


def make_dps_table(parse_reader, eq_class=None, first=1, last=sys.maxsize):
    return make_parse_db(parse_reader).get_dps_table(first=first, last=last)

def make_parse_db(parse_reader):
    pdb = parsedb.ParseDB(parse_reader.aliases, dps_reader=parse_reader)
    return pdb

def print_table_with_formatter(fm, dtab):
    ts = format_table_with_formatter(fm, dtab)
    tf.print_table(ts)

def format_table_with_formatter(fm, table):
    ts = tf.TableStrings()

    ts.title = fm.format_title(table.title)

    ts.table_start = fm.table_start()
    ts.table_stop = fm.table_stop()

    if table.is_cast:
        pass                            ## TODO:
    else:
        labels = list(table.column_labels)
        ts.headers = fm.format_labels([''] + labels)

        srow = table.rows[0]
        #              pos    name         sdps                     dmg                      dps                       pct           cls     gid   grp
        dps_summary = [''] + [srow[0]] + [tf.humanize(srow[1])] + [tf.humanize(srow[2])] + [tf.humanize(srow[3])] + [str(srow[4])] + [''] + [''] + ['']
        ts.headers.append(fm.format_summary_row(dps_summary))

        ts.rows = fm.format_data_rows(table.rows[1:])

    return ts

class TtyDPSFormatter:
    #          pos char_name   sdps   dmg    dps          % char_cls     grp   classes
    #               Cilenne                                     BRD       10   (6-1)*3 + (6-1-1)*2
    #                                                                          6 slots x~ "BRD, "
    dpsrow = '{0:>2} {1:>20} {2:>7} {3:>7} {4:>7}   {5:<5}%   {6:<3}   {7:>2}  {8:<19}'
    row_sep = ' '

    def format_title(self, title):
        return title

    def table_start(self):
        return ''
    def table_stop(self):
        return ''

    def format_labels(self, labels):
        return [TtyDPSFormatter.dpsrow.format(*labels)]

    def format_summary_row(self, dps_summary):
        return TtyDPSFormatter.dpsrow.format(*dps_summary)

    def format_data_rows(self, rows):
#        for i, tr in enumerate(rows):
#            y = [
#                    str(i + 1),                     # position
#                ] + [
#                    str(tr[0]),                     # name
#                ] + [
#                    tf.humanize(str(tr[1])),        # sdps
#                ] + [
#                    tf.humanize(str(tr[2])),        # dmg
#                ] + [
#                    tf.humanize(str(tr[3])),        # dps
#                ] + [
#                    str(tr[4])                      # %
#                ] + [
#                    tr[5]                           # char class
#                ] + [
#                    str(tr[6])                      # group #
#                ] + [
#                    tr[7]                           # group member classes
#                ]
#            pp.pprint(y)
#            x = TtyDPSFormatter.dpsrow.format(*y)
#            pp.pprint(x)

        return [
            TtyDPSFormatter.dpsrow.format(*
                [
                    str(i + 1),                     # position
                ] + [
                    str(tr[0]),                     # name
                ] + [
                    tf.humanize(str(tr[1])),        # sdps
                ] + [
                    tf.humanize(str(tr[2])),        # dmg
                ] + [
                    tf.humanize(str(tr[3])),        # dps
                ] + [
                    str(tr[4])                      # %
                ] + [
                    tr[5]                           # char class
                ] + [
                    str(tr[6])                      # group #
                ] + [
                    tr[7]                           # group member classes
                ]
            ) for i, tr in enumerate(rows)
        ]


class EnjinDPSFormatter:
    dpsrow = '[tr][td]{0}[/td][/tr]'
    row_sep = '[/td][td]'

    header = '[tr][td][b]{0}[/b][/td][/tr]'
    header_sep = '[/b][/td][td][b]'

    title = '[size=5][b]{0}[/b][/size]'

    def _format_enjin_header(self, *args):
        return EnjinDPSFormatter.header.format(EnjinDPSFormatter.header_sep.join(args))

    def format_title(self, title):
        return EnjinDPSFormatter.title.format(title)

    def table_start(self):
        return '[table]'
    def table_stop(self):
        return '[/table]'

    def format_labels(self, labels):
        return [self._format_enjin_header(*(labels))]

    def format_summary_row(self, dps_summary):
        return self._format_enjin_header(*dps_summary)

    def format_data_rows(self, rows):
        return [EnjinDPSFormatter.dpsrow.format(
            EnjinDPSFormatter.row_sep.join(
                [
                    str(i + 1),                     # position
                ] + [
                    str(tr[0]),                     # name
                ] + [
                    tf.humanize(str(tr[1])),        # sdps
                ] + [
                    tf.humanize(str(tr[2])),        # dmg
                ] + [
                    tf.humanize(str(tr[3])),        # dps
                ] + [
                    str(tr[4])                      # %
                ] + [
                    tr[5]                           # char class
                ] + [
                    str(tr[6])                      # group #
                ] + [
                    tr[7]                           # group member classes
                ]
            )
        ) for i, tr in enumerate(rows)]
