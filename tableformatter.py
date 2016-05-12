import parsedb


class ParseTable:
    def __init__(self):
        self.title = ''
        self.table_start = ''
        self.table_stop = ''
        self.headers = []
        self.rows = []


def print_table(table: ParseTable):
    print(table.title)
    if table.table_start:
        print(table.table_start)
    for header in table.headers:
        print(header)
    for row in table.rows:
        print(row)
    if table.table_stop:
        print(table.table_stop)


def format_enjin_table(table: parsedb.CastTable):
    header = '[tr][td][b]{0}[/b][/td][/tr]'
    header_sep = '[/b][/td][td][b]'

    row = '[tr][td]{0}[/td][/tr]'
    row_sep = '[/td][td]'

    pt = ParseTable()
    pt.title = '[size=5][b]{0}[/b][/size]'.format(table.class_name)
    pt.table_start = '[table]'
    pt.table_stop = '[/table]'
    pt.headers = [header.format(header_sep.join([''] + table.get_players()))]
    pt.headers.append(header.format(header_sep.join(['Total'] + [str(x) for x in table.get_totals()])))
    spells = table.get_spells()
    t_rows = table.get_rows()
    pt.rows = [row.format(row_sep.join([spells[i]] + [str(x) for x in tr])) for i, tr in enumerate(t_rows)]

    return pt


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
