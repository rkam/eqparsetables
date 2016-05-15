import sqlite3
import everquestinfo as eq

import itertools as it
import operator as op
import collections as co
import sys


class ParseTable:
    def __init__(self, title, column_labels, rows, is_cast=False):
        self.title = title
        self.column_labels = column_labels
        self.rows = rows
        self.is_cast = is_cast

    def get_spell_totals(self):
        return [sum(x) for x in zip(*[c[1:] for c in self.rows])]


class ParseDB:
    def __init__(self, config, caster_dod={}, dps_reader=None):
        self.config = config
        self.caster_dod = caster_dod
        self.dps_reader = dps_reader

        self.conn = sqlite3.connect(':memory:')
        self.cur = self.conn.cursor()

        self.create_player_table()
        self.create_cast_tables()
        self.create_dps_table()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def create_player_table(self):
        self.cur.execute('CREATE TABLE players ('
                         '  name TEXT NOT NULL, '
                         '  class TEXT NOT NULL, '
                         '  alias TEXT NOT NULL'
                         ')')
        for player in self.config.items():
            self.cur.execute('INSERT INTO players (name, class, alias) VALUES (?, ?, ?)', (player[0],
                                                                                           player[1]['class'],
                                                                                           player[1]['alias']))

    def create_cast_tables(self):
        self.cur.execute('CREATE TABLE casts ('
                         '  player TEXT NOT NULL, '
                         '  spell TEXT NOT NULL, '
                         '  count INTEGER(5) DEFAULT 0'
                         ')')
        for player in self.caster_dod.items():
            for spell in player[1]:
                self.cur.execute('INSERT INTO casts '
                                 '(player, spell, count) '
                                 'VALUES (?, ?, ?)',
                                 (player[0], spell, player[1][spell]))

    def update_cast_parse(self, dod):
        for player in dod.items():
            for spell in player[1]:
                self.cur.execute('INSERT OR REPLACE INTO casts (player, spell, count) '
                                 'VALUES (?, ?, ?)',
                                 (player[0], spell, player[1][spell]))

    def create_dps_table(self):
        self.cur.execute('CREATE TABLE deeps ('
                         '  player TEXT NOT NULL, '
                         '  damage INTEGER(10), '
                         '  sdps INTEGER(10), '
                         '  dps INTEGER(10), '
                         '  time INTEGER(10), '
                         '  percentage INTEGER(3)'
                         ')')

        if self.dps_reader:
            for pl in self.dps_reader.dpser_dod.items():
                self.cur.execute('INSERT INTO deeps '
                                 '(player, damage, sdps, dps, time, percentage) '
                                 'VALUES(?, ?, ?, ?, ?, ?)',
                                 (pl[0], pl[1]['total'], pl[1]['sdps'], pl[1]['dps'], pl[1]['time'], pl[1]['pct']))

    def get_cast_table(self, eq_class):
        self.cur.execute('SELECT spell, name, count '
                         'FROM (SELECT name FROM players WHERE class=?) '
                         'JOIN casts ON name=casts.player;', (eq_class, ))
        data = self.cur.fetchall()
        players = sorted(set(row[1] for row in data))
        pivot = ((spell, co.defaultdict(lambda: None, (it.islice(d, 1, None) for d in data)))
                 for spell, data in it.groupby(sorted(data), op.itemgetter(0)))

        rows = [[spell] + [casts.get(p, 0) for p in players] for spell, casts in pivot]
        return ParseTable(eq.eq_classes.get(eq_class), [''] + players, rows, is_cast=True)

    def get_dps_table(self, eq_class=None, first=1, last=sys.maxsize):
        if eq_class:
            self.cur.execute('SELECT p.name, d.sdps, d.damage, d.percentage '
                             'FROM (SELECT name FROM players WHERE class=?) p '
                             'JOIN deeps d ON  p.name=d.player '
                             'ORDER BY d.sdps DESC;', (eq_class, ))
        else:
            self.cur.execute('SELECT player, sdps, damage, percentage FROM deeps ORDER BY sdps DESC')
        data = self.cur.fetchall()[first - 1: last]
        stats = self.dps_reader.guild_stats
        rows = [("Raid", stats['sdps'], stats['total'], stats['pct'])] + [x for x in data]
        columns = ['', 'SDPS', 'Total DMG', 'Percentage']
        title = '{0} in {1} on {2}'.format(*self.dps_reader.get_info())
        return ParseTable(title, columns, rows)
