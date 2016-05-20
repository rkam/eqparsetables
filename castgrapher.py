import os
import operator as op
import pygal as pg
import parsedb
import everquestinfo as eq


def graph_heals(table: parsedb.ParseTable, separate_spells=False):
    if table.title not in ['Clerics', 'Druids', 'Shamans']:
        print('Heal graphs cannot be generated from the {0} table.'.format(table.title))
        return

    blast_chart = pg.StackedBar()
    blast_chart.title = table.title + ': Heals'
    blast_chart.x_labels = table.column_labels[1:]

    if separate_spells:
        heals = (row for row in table.rows if row[0] in eq.blast_heals.keys())
        for spell in heals:
            blast_chart.add(spell[0], spell[1:])
    else:
        healtypes = {}
        for row in table.rows:
            t = eq.blast_heals.get(row[0], '')
            if t:
                healtypes[t] = map(op.add, healtypes.get(t, [0] * len(row[1:])), row[1:])
        for heal in healtypes.keys():
            blast_chart.add(heal, healtypes[heal])
    blast_chart.render_to_file(os.getcwd() + '/' + table.title.lower() + '_heals.svg')

    return


def graph_utilities(table: parsedb.ParseTable, separate_spells=False):
    if table.title not in ['Clerics', 'Druids', 'Shamans']:
        print('Utility graphs cannot be generated from the {0} table.'.format(table.title))
        return

    utility_chart = pg.StackedBar()
    utility_chart.title = table.title + ': Utility Spells'
    utility_chart.x_labels = table.column_labels[1:]

    if separate_spells:
        utilities = [row for row in table.rows if row[0] in eq.utilities.keys()]
        for spell in utilities:
            utility_chart.add(spell[0], spell[1:])
    else:
        utiltypes = {}
        for row in table.rows:
            t = eq.utilities.get(row[0], '')
            if t:
                utiltypes[t] = map(op.add, utiltypes.get(t, [0] * len(row[1:])), row[1:])
        for util in utiltypes.keys():
            utility_chart.add(util, utiltypes[util])

    utility_chart.render_to_file(os.getcwd() + '/' + table.title.lower() + '_utilities.svg')

    return


def graph_nukes(table: parsedb.ParseTable, separate_spells=True):
    if table.title not in ['Clerics', 'Druids', 'Shamans']:
        print('Nuke graphs cannot be generated from the {0} table.'.format(table.title))
        return

    nuke_chart = pg.StackedBar()
    nuke_chart.title = table.title + ': Nuke Spells'
    nuke_chart.x_labels = table.column_labels[1:]

    if separate_spells:
        utilities = [row for row in table.rows if row[0] in eq.nukes.keys()]
        for spell in utilities:
            nuke_chart.add(spell[0], spell[1:])
    else:
        nukes = {}
        for row in table.rows:
            t = eq.nukes.get(row[0], '')
            if t:
                nukes[t] = map(op.add, nukes.get(t, [0] * len(row[1:])), row[1:])
        for nuke in nukes.keys():
            nuke_chart.add(nuke, nukes[nuke])

    nuke_chart.render_to_file(os.getcwd() + '/' + table.title.lower() + '_nukes.svg')

    return


def generate_class_graphs(table: parsedb.ParseTable):
    dispatch = {
        'Clerics': [graph_heals, graph_utilities],
        'Druids': [graph_heals, graph_utilities, graph_nukes]
    }
    for f in dispatch.get(table.title, []):
        f(table)
