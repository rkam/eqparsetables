import parsedb


class TableStrings:
    def __init__(self):
        self.title = ''
        self.table_start = ''
        self.table_stop = ''
        self.headers = []
        self.rows = []


def print_table(table: TableStrings):
    print(table.title)
    if table.table_start:
        print(table.table_start)
    for header in table.headers:
        print(header)
    for row in table.rows:
        print(row)
    if table.table_stop:
        print(table.table_stop)


def format_enjin_table(table: parsedb.ParseTable):
    header = '[tr][td][b]{0}[/b][/td][/tr]'
    header_sep = '[/b][/td][td][b]'

    row = '[tr][td]{0}[/td][/tr]'
    row_sep = '[/td][td]'

    ts = TableStrings()
    ts.title = '[size=5][b]{0}[/b][/size]'.format(table.title)
    ts.table_start = '[table]'
    ts.table_stop = '[/table]'
    if table.is_cast:
        ts.headers = [header.format(header_sep.join(table.column_labels))]
        total_header = ['Total'] + list(map(str, table.get_spell_totals()))
        ts.headers.append(format_enjin_header(*total_header))
        ts.rows = [format_enjin_row(*map(str, tr)) for tr in table.rows]
    else:
        ts.headers = [format_enjin_header(*([''] + table.column_labels))]
        dps_summary = [''] + [(table.rows[0])[0]] + [humanize(str(x)) for x in (table.rows[0])[1:-1]] + \
                      [str((table.rows[0])[-1]) + '%']
        ts.headers.append(format_enjin_header(*dps_summary))
        ts.rows = [row.format(row_sep.join([str(i + 1)] + [str(tr[0])] + [humanize(str(x)) for x in tr[1:-1]] +
                                           [str(tr[-1]) + '%'])) for i, tr in enumerate(table.rows[1:])]

    return ts


def format_enjin_header(*args):
    """
    Formats a row of data with bolded values.

    :param args: the values to be formatted
    :return: a string corresponding to a row in enjin table format
    """
    header = '[tr][td][b]{0}[/b][/td][/tr]'
    header_sep = '[/b][/td][td][b]'
    return header.format(header_sep.join(args))


def format_enjin_row(*args):
    """
    Formats a row of data into enjin table format.

    :param args: the values to be formatted
    :return: a string corresponding to a row in enjin table format
    """
    row = '[tr][td]{0}[/td][/tr]'
    row_sep = '[/td][td]'
    return row.format(row_sep.join(args))


def format_tty_table(table: parsedb.ParseTable):
    row = '{0:35}{1}'
    dpsrow = '{0:>2} {1:>20} {2:>15} {3:>10}   {4:<4}'

    ts = TableStrings()
    ts.title = table.title
    if table.is_cast:
        ts.headers = [row.format(table.column_labels[0], ''.join('{:15}'.format(x) for x in table.column_labels[1:]))]
        ts.headers.append(row.format('Total', ''.join(['{:15}'.format(str(x)) for x in table.get_spell_totals()])))
        ts.rows = [row.format(tr[0], ''.join(['{:15}'.format(str(x)) for x in tr[1:]])) for tr in table.rows]
    else:
        labels = [''] + list(table.column_labels)
        srow = table.rows[0]
        summary = ['__Raid__'] + [humanize(srow[1])] + [humanize(srow[2])] + [str(srow[3]) + '%']
        ts.headers = [dpsrow.format(*labels)]
        ts.headers.append(dpsrow.format('', *summary))
        ts.rows = [dpsrow.format(i + 1, r[0], humanize(r[1]), humanize(r[2]), str(r[3]) + '%') for i, r in enumerate(table.rows[1:])]

    return ts


def humanize(s):
    suffix = ['', 'k', 'm', 'bn', 'tn']
    n = float(s)
    if n < 1000:
        return s
    mag = 0
    while n > 1000:
        n /= 1000.0
        mag += 1
    return '{0:.1f}{1}'.format(n, suffix[mag])

def comma_number(s):
    n = int(s)
    if n < 1000:
        return str(n)

    m = int(n % 1000) 
    if m < 100:
        r = '0' + str(m)
    else:
        r = str(m)

    while n > 1000:
        n = int(n / 1000)
        m = int(n % 1000) 
        if m < 100 and n > 1000:
            r = '0' + str(m) + "," + r
        else:
            r = str(m) + "," + r
    return r
