import os
import operator as op
import pygal as pg
import parsedb
import everquestinfo as eq


class SpellFilter:
    def __init__(self, name, spells):
        self.name = name
        self.spells = spells


def graph_heals(table: parsedb.ParseTable, separate_spells=False):
    if table.title not in ['Clerics', 'Druids', 'Shamans']:
        print('Heal graphs cannot be generated from the {0} table.'.format(table.title))
        return

    heal_filter = SpellFilter('Heals', eq.blast_heals)
    graph_spells(table, heal_filter, separate_spells)

    return


def graph_utilities(table: parsedb.ParseTable, separate_spells=False):
    if table.title not in ['Clerics', 'Druids', 'Shamans']:
        print('Utility graphs cannot be generated from the {0} table.'.format(table.title))
        return

    utility_filter = SpellFilter('Utility Spells', eq.utilities)
    graph_spells(table, utility_filter, separate_spells)

    return


def graph_nukes(table: parsedb.ParseTable, separate_spells=True):
    if table.title not in ['Druids']:
        print('Nuke graphs cannot be generated from the {0} table.'.format(table.title))
        return

    nuke_filter = SpellFilter('Nukes', eq.nukes)
    graph_spells(table, nuke_filter, separate_spells)

    return


def graph_spells(table: parsedb.ParseTable, spell_filter, separate_spells=False):
    chart = pg.StackedBar()
    chart.title = '{0}: {1}'.format(table.title, spell_filter.name)
    chart.x_labels = table.column_labels[1:]

    if separate_spells:
        spells = [row for row in table.rows if row[0] in spell_filter.spells.keys()]
        for spell in spells:
            chart.add(spell[0], spell[1:])
    else:
        spell_types = {}
        for row in table.rows:
            t = spell_filter.spells.get(row[0], '')
            if t:
                spell_types[t] = map(op.add, spell_types.get(t, [0] * len(row[1:])), row[1:])
        for spell_type in spell_types.keys():
            chart.add(spell_type, spell_types[spell_type])

    chart.render_to_file('{0}/{1}_{2}.svg'.format(os.getcwd(), table.title.lower(), spell_filter.name.lower()))

    return


def generate_class_graphs(table: parsedb.ParseTable):
    dispatch = {
        'Clerics': [graph_heals, graph_utilities],
        'Druids': [graph_heals, graph_utilities, graph_nukes],
        'Shamans': [graph_heals, graph_utilities]
    }
    for f in dispatch.get(table.title, []):
        f(table)
