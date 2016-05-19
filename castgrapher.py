import os
import pygal as pg
import parsedb
import everquestinfo as eq


def zero_to_none(x):
    if x == 0:
        return None
    else:
        return x


def graph_heals(table: parsedb.ParseTable):
    if table.title not in ['Clerics', 'Druids', 'Shamans']:
        print('Heal graphs cannot be generated from the {0} table.'.format(table.title))

    heals = [row for row in table.rows if row[0] in eq.blast_heals]

    blast_chart = pg.StackedBar()
    blast_chart.title = table.title + ' Single-Target Heals'
    blast_chart.x_labels = table.column_labels[1:]
    for spell in heals:
        blast_chart.add(spell[0], list(map(zero_to_none, spell[1:])))
    blast_chart.render_to_file(os.getcwd() + '/' + table.title.lower() + '_blasts.svg')

    return


def graph_utilities(table: parsedb.ParseTable):
    if table.title not in ['Clerics', 'Druids', 'Shamans']:
        print('Utility graphs cannot be generated from the {0} table.'.format(table.title))

    utilities = [row for row in table.rows if row[0] in eq.utilities.keys()]

    utility_chart = pg.StackedBar()
    utility_chart.title = table.title + ' Utility Spells'
    utility_chart.x_labels = table.column_labels[1:]
    for spell in utilities:
        utility_chart.add(spell[0], spell[1:])
    utility_chart.render_to_file(os.getcwd() + '/' + table.title.lower() + '_utilities.svg')

    return


def graph_nukes(table: parsedb.ParseTable):
    return


def generate_class_graphs(table: parsedb.ParseTable):
    dispatch = {
        'Clerics': [graph_heals, graph_utilities],
        'Druids': [graph_heals, graph_utilities, graph_nukes]
    }
    for f in dispatch.get(table.title, []):
        f(table)
