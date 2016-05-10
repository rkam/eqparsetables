import parsedb
import sys


def print_cast_table(table: parsedb.CastTable):
    print('{0}'.format(table.class_name))
    print('')
    print(make_header('', *table.get_players()))
    print(make_header('Total', *[str(x) for x in table.get_totals()]))
    spells = table.get_spells()
    for i, row in enumerate(table.get_rows()):
        print(make_row(spells[i], *[str(x) for x in row]))
    print('')


def print_cast_tables(tables: [parsedb.CastTable]):
    """
    Print all parsed class tables in a plain text table format.

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
    print('')
    print('{0} in {1} seconds on {2}'.format(*fight_info.info()))
    print(make_header('', '', 'SDPS', 'Total DMG', 'Percentage'))
    print(make_header('', '__Raid__', humanize(stats['sdps']), humanize(stats['total']), stats['pct'] + '%'))
    for rank, player in enumerate(sorted(dpser_dod.items(), key=lambda x: int(x[1]['sdps']), reverse=True)):
        if rank + 1 < start:
            continue
        elif rank + 1 > stop:
            break
        print(make_row(str(rank + 1), player[0], humanize(player[1]['sdps']), humanize(player[1]['total']),
                       player[1]['pct'] + '%'))
    print('')


def make_header(*args):
    """
    Formats a row of data with bolded values.

    :param args: the values to be formatted
    :return: a string corresponding to a row in a plain text table format
    """
    return make_row(*args)


def make_row(*args):
    """
    Formats a row of data into a plain text table format.

    :param args: the values to be formatted
    :return: a string corresponding to a row in a plain text table format
    """
    sys.stdout.write("%2s %20s %15s %10s   %4s" % (args))
    return ""


def humanize(s):
    suffix = ['', 'k', 'm', 'bn', 'tn']

    if int(s) < 1000:
        return s

    n = float(s)
    mag = 0
    while n > 1000:
        n /= 1000.0
        mag += 1
    return '{0:.1f}{1}'.format(n, suffix[mag])
