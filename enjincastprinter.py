import parsedb
import sys


def print_cast_table(table: parsedb.CastTable):
    print('[size=5][b]{0}[/b][/size]'.format(table.class_name))
    print('[table]')
    print(make_header('', *table.get_players()))
    print(make_header('Total', *[str(x) for x in table.get_totals()]))
    spells = table.get_spells()
    for i, row in enumerate(table.get_rows()):
        print(make_row(spells[i], *[str(x) for x in row]))
    print('[/table]')


def print_cast_tables(tables: [parsedb.CastTable]):
    """
    Print all parsed class tables in enjin forum table format.

    :param tables: list of CastTables to be printed
    :return: void
    """
    for loop_count, table in enumerate(tables):
        padding = '\n\n' if loop_count else ''
        print(padding)
        print_cast_table(table)


def print_dps_table(fight_info, start=1, stop=sys.maxsize):
    stats = fight_info.guild_stats
    dpser_dod = fight_info.dpser_dod
    print('[size=5][b]{0} in {1} seconds on {2}[/b][/size]'.format(*fight_info.info()))
    print('[table]')
    print(make_header('', '', 'SDPS', 'Total DMG', 'Percentage'))
    print(make_header('', 'Raid', humanize(stats['sdps']), humanize(stats['total']), stats['pct'] + '%'))
    for rank, player in enumerate(sorted(dpser_dod.items(), key=lambda x: int(x[1]['sdps']), reverse=True)):
        if rank + 1 < start:
            continue
        elif rank + 1 > stop:
            break
        print(make_row(str(rank + 1), player[0], humanize(player[1]['sdps']), humanize(player[1]['total']),
                       player[1]['pct'] + '%'))
    print('[/table]')


def make_header(*args):
    """
    Formats a row of data with bolded values.

    :param args: the values to be formatted
    :return: a string corresponding to a row in enjin table format
    """
    header = '[tr][td][b]{0}[/b][/td][/tr]'
    header_sep = '[/b][/td][td][b]'
    return header.format(header_sep.join(args))


def make_row(*args):
    """
    Formats a row of data into enjin table format.

    :param args: the values to be formatted
    :return: a string corresponding to a row in enjin table format
    """
    row = '[tr][td]{0}[/td][/tr]'
    row_sep = '[/td][td]'
    return row.format(row_sep.join(args))


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
