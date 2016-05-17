import os
import pygal as pg
import parsedb
import everquestinfo as eq


def zero_to_none(x):
    if x == 0:
        return None
    else:
        return x


def graph_clerics(table: parsedb.ParseTable):
    if table.title != 'Clerics':
        print('Cleric graphs cannot be generated from the {0} table.'.format(table.title))

    blasts = []
    utilities = []
    # heal_alts = []
    # utility_alts = []
    # nuke_alts = []

    for row in table.rows:
        if row[0] in eq.cleric_blast_heals:
            blasts.append(row)
        elif row[0] in eq.cleric_utilities:
            utilities.append(row)

    blast_chart = pg.StackedBar()
    blast_chart.title = 'Cleric Single-Target Heals'
    blast_chart.x_labels = table.column_labels[1:]
    for spell in blasts:
        blast_chart.add(spell[0], list(map(zero_to_none, spell[1:])))
    blast_chart.render_to_file(os.getcwd() + '/cleric_blasts.svg')

    utility_chart = pg.StackedBar()
    utility_chart.title = 'Cleric Utility Spells'
    utility_chart.x_labels = table.column_labels[1:]
    for spell in utilities:
        utility_chart.add(spell[0], spell[1:])
    utility_chart.render_to_file(os.getcwd() + '/cleric_utilities.svg')

    return

