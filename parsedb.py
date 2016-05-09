import sqlite3
import everquestinfo as eq


class CastTable:
    def __init__(self, eq_class, cast_data, spell_data):
        """
        Construct a CastTable object

        :param eq_class: the EQ class of the players to appear in the CastTable (e.g. 'CLR')
        :param cast_data: a list of lists of the form [[player_name, spell_1, spell_2, ..., spell_n]_1, ...]
        :param spell_data: a list of spell names corresponding to the spells in cast_data
        :return: a CastTable object
        """
        self.class_name = eq.eq_classes.get(eq_class, 'unknown')
        self.casts = sorted(cast_data)
        self.spells = spell_data

    def get_rows(self):
        return zip(*[x[1:] for x in self.casts])

    def get_players(self):
        return [x[0] for x in self.casts]

    def get_totals(self):
        return [sum(x[1:]) for x in self.casts]

    def get_spells(self):
        return self.spells


class ParseDB:
    def __init__(self, spells_cast_by_class, classes_parsed, caster_dod, config):
        self.spells_cast_by_class = spells_cast_by_class
        self.classes_parsed = classes_parsed
        self.caster_dod = caster_dod
        self.config = config

        self.conn = sqlite3.connect(':memory:')
        self.cur = self.conn.cursor()

        self.create_class_tables()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def create_class_tables(self):
        """
        Create a table for each class with unique spell names as columns and casters as rows.

        :return: void
        """
        for eq_class in self.classes_parsed:
            class_name = eq.eq_classes.get(eq_class, 'unknown')
            class_spells = ', '.join('"{0}" INTEGER(5) DEFAULT 0'.format(spell)
                                     for spell in sorted(self.spells_cast_by_class[eq_class]))
            self.cur.execute("CREATE TABLE %s (player TEXT NOT NULL, %s);" % (class_name, class_spells))

        for caster, cast in self.caster_dod.items():
            class_name = eq.eq_classes.get(self.config[caster]['class'], 'unknown')
            spells_cast = sorted(list(self.caster_dod[caster].keys()))
            cast_counts = [cast[spell] for spell in spells_cast]
            self.cur.execute("INSERT INTO %s (player, %s) VALUES (%s, %s);" % (
                class_name, ", ".join('"{0}"'.format(spell) for spell in spells_cast), '"{0}"'.format(caster),
                ", ".join(cast_counts)))

    def get_cast_table(self, eq_class):
        """
        Create the cast parse table of a single class.

        :param eq_class: The EQ abbreviation of the desired class
        :return: a ParseTable containing the casting information recorded for all members of a given class
        """
        return CastTable(eq_class, self.get_all(eq_class), self.get_spells(eq_class))

    def get_players(self, eq_class):
        class_name = eq.eq_classes.get(eq_class, 'unknown')
        self.cur.execute('SELECT player FROM %s' % class_name)
        return self.cur.fetchall()

    def get_totals(self, eq_class):
        class_name = eq.eq_classes.get(eq_class, 'unknown')
        table_spells = sorted(self.spells_cast_by_class[eq_class])
        player_total = '("{0}") AS Total'.format('" + "'.join(table_spells))
        self.cur.execute('SELECT player, %s FROM %s' % (player_total, class_name))
        return self.cur.fetchall()

    def get_spells(self, eq_class):
        class_name = eq.eq_classes.get(eq_class, 'unknown')
        self.cur.execute('PRAGMA TABLE_INFO(%s)' % class_name)
        return [row[1] for row in self.cur.fetchall()[1:]]

    def get_all(self, eq_class):
        class_name = eq.eq_classes.get(eq_class, 'unknown')
        self.cur.execute('SELECT * FROM %s' % class_name)
        return self.cur.fetchall()
