import sqlite3
import collections
import operator
import everquestinfo as eq


class ParseTable:
    def __init__(self, db_cursor):
        self.cur = db_cursor
        pass

    def __iter__(self):
        pass

    def __next__(self):
        pass

    def getHeader(self):
        pass

    def getTotals(self):
        pass


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

    def get_class_table(self, eq_class):
        """
        Create the parse table of a single class.

        :param eq_class: The EQ abbreviation of the class to be printed
        :return: none
        """
        class_name = eq.eq_classes.get(eq_class, 'unknown')
        table_spells = sorted(self.spells_cast_by_class[eq_class])
        spell_query = '"{0}"'.format('","'.join(table_spells))
        self.cur.execute('SELECT player, %s FROM %s;' % (spell_query, class_name))
        rows = self.cur.fetchall()

        print('[size=5][b]{0}[/b][/size]'.format(class_name))

        db_data = []
        for i, row in enumerate(rows):
            db_data.append([d for d in row])

        column_names = [str(d[0]) for d in self.cur.description]
        column_names[0] = ''
        all_data = collections.deque(sorted(db_data, key=operator.itemgetter(0)))
        all_data.appendleft(column_names)

        print('[table]')
        for j, column in enumerate(all_data[0]):
            if j is 0 or j is 1:
                print('[tr][td][b]{0}[/b][/td][/tr]'.format('[/b][/td][td][b]'.join(str(row[j]) for row in all_data)))
            else:
                print('[tr][td]{0}[/td][/tr]'.format('[/td][td]'.join(str(row[j]) for row in all_data)))
        print('[/table]')

    def get_players(self, eq_class):
        class_name = eq.eq_classes.get(eq_class, 'unknown')
        self.cur.execute('SELECT player FROM %s' % class_name)
        return self.cur.fetchall()

    def get_totals(self, eq_class):
        class_name = eq.eq_classes.get(eq_class, 'unknown')
        table_spells = sorted(self.spells_cast_by_class[eq_class])
        player_total = '("{0}") AS Total'.format('" + "'.join(table_spells))
        # query = "SELECT %s FROM %s;"
        # self.cur.execute(query, (player_total, class_name))
        self.cur.execute('SELECT %s FROM %s' % (player_total, class_name))
        return self.cur.fetchall()

    def get_all(self, eq_class):
        class_name = eq.eq_classes.get(eq_class, 'unknown')
        self.cur.execute('SELECT * FROM %s' % class_name)
        return self.cur.fetchall()
