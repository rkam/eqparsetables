import sys
import gpcastreader as gpc


def print_dps_table(reader: gpc.GPDPSReader, start=1, stop=sys.maxsize):
    stats = reader.guild_stats
    dpser_dod = reader.dpser_dod
    print('[size=5][b]{0} in {1} seconds on {2}[/b][/size]'.format(*reader.get_info()))
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
