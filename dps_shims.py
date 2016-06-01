import sys
import dps_parse_db as parsedb
import tableformatter as tf

_err_explan1a = "Found unassociated pet"
_err_explan1b = ": This means that GamParse didn't link the pet, so the parser rolled that pet's stats into the owner's stats."
_err_explan2a = "Unrecognized player blah-blah-blah"
_err_explan2b = ": This means neither GamParse nor I know whose pet that is, so it's ignored."

def make_dps_table(parse_reader, eq_class=None, first=1, last=sys.maxsize):
    return make_parse_db(parse_reader).get_dps_table(first=first, last=last)

def make_parse_db(parse_reader):
    pdb = parsedb.ParseDB(parse_reader.aliases, dps_reader=parse_reader)
    return pdb

def print_table_with_formatter(fm, dtab, errs):
    ts = format_table_with_formatter(fm, dtab)
    tf.print_table(ts)

    if len(errs):
        ets = format_errs_with_formatter(fm, errs)
        tf.print_table(ets)

def format_table_with_formatter(fm, table):
    ts = tf.TableStrings()

    ts.title = fm.format_title(table.title)

    ts.table_start = fm.table_start()
    ts.table_stop = fm.table_stop()

    if table.is_cast:
        pass                            ## TODO:
    else:
        ts.headers = fm.format_labels([''] + list(table.column_labels))

        srow = table.rows[0]
        #              pos    name         sdps                     dmg                      dps                       pct           cls     gid   grp
        dps_summary = [''] + [srow[0]] + [tf.humanize(srow[1])] + [tf.humanize(srow[2])] + [tf.humanize(srow[3])] + [str(srow[4])] + [''] + [''] + ['']
        ts.headers.append(fm.format_summary_row(dps_summary))

        ts.rows = fm.format_data_rows(table.rows[1:])

    return ts

def format_errs_with_formatter(fm, errs):
    ts = tf.TableStrings()

    ts.table_start = fm.errors_start()
    ts.table_stop = fm.errors_stop()

    ts.headers = fm.format_errors(errs)
    ts.rows = fm.format_addendum()

    return ts


class TtyDPSFormatter:

    #            pos   name   sdps    dmg    dps      %         cls      gid    group
    dpsrow = '{0:>2} {1:>20} {2:>7} {3:>7} {4:>7}   {5:<5}%   {6:<3}   {7:>2}  {8:<19}'
    # group: 6 classes/group  -> ("BRD, ..., ROG")  ==> 6*3 + (6-1)*2

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
        return [TtyDPSFormatter.dpsrow.format(*
            _make_dps_row(i, tr)
        ) for i, tr in enumerate(rows)]

    def errors_start(self):
        return '\n'
    def errors_stop(self):
        return ''
    def format_errors(self, errs):
        return errs
    def format_addendum(self):
        return [
            "",
            _err_explan1a + _err_explan1b,
            _err_explan2a + _err_explan2b,
         ]


class EnjinDPSFormatter:

    def format_title(self, title):
        return '[size=5][b]{0}[/b][/size]'.format(title)

    def table_start(self):
        return '[table]'
    def table_stop(self):
        return '[/table]'

    def _format_header(self, *args):
        return '[tr][td][b]{0}[/b][/td][/tr]'.format(
                    '[/b][/td][td][b]'.join(args)
                )

    def format_labels(self, labels):
        return [self._format_header(*(labels))]

    def format_summary_row(self, dps_summary):
        return self._format_header(*dps_summary)

    def format_data_rows(self, rows):
        return [
            '[tr][td]{0}[/td][/tr]'.format(
                '[/td][td]'.join(_make_dps_row(i, tr))
            ) for i, tr in enumerate(rows)]

    def errors_start(self):
        return '\n[size=2]'
    def errors_stop(self):
        return '[/size]'
    def format_errors(self, errs):
        return errs
    def format_addendum(self):
        return [
            "",
            "[color=#239edd]" + _err_explan1a + "[/color]" + _err_explan1b,
            "[color=#239edd]" + _err_explan2a + "[/color]" + _err_explan2b,
         ]

def _make_dps_row(i, tr):
    return  [
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
