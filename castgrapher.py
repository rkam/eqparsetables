import os
import operator as op
import pygal as pg
import parsedb
import everquestinfo as eq


class SpellFilter:
    """
    A simple container class used to classify spells.
    """
    def __init__(self, name, spells):
        """
        Construct a SpellFilter object.

        :param name: the name of the spell type, e.g. "Heals"
        :param spells: a list of spells of type 'name'
        """
        self.name = name
        self.spells = spells


def graph_heals(table: parsedb.ParseTable, separate_spells=False):
    """
    Gather up heal spells and create healing graphs for each priest class.

    :param table: ParseDB cast table
    :param separate_spells: flag specifying whether heals should be grouped by type or named individually
    :return: void
    """
    if table.title not in ['Clerics', 'Druids', 'Shamans']:
        print('Heal graphs cannot be generated from the {0} table.'.format(table.title))
        return

    if not table.is_cast:
        print('Cannot generate heal graphs from non-cast table.')
        return

    heal_filter = SpellFilter('Heals', eq.heals)
    graph_spells(table, heal_filter, separate_spells)

    return


def graph_utilities(table: parsedb.ParseTable, separate_spells=False):
    """
    Gather up utility spells and create healing graphs for each priest class.

    :param table: ParseDB cast table
    :param separate_spells: flag specifying whether utility spells should be grouped by type or named individually
    :return: void
    """
    if table.title not in ['Clerics', 'Druids', 'Shamans']:
        print('Utility graphs cannot be generated from the {0} table.'.format(table.title))
        return

    if not table.is_cast:
        print('Cannot generate utility graphs from non-cast table.')

    utility_filter = SpellFilter('Utility', eq.utilities)
    graph_spells(table, utility_filter, separate_spells)

    return


def graph_nukes(table: parsedb.ParseTable, separate_spells=False):
    """
    Gather up direct damage spells and create healing graphs for each priest class.

    :param table: ParseDB cast table
    :param separate_spells: flag specifying whether nukes should be grouped by type or named individually
    :return: void
    """
    if table.title not in ['Druids']:
        print('Nuke graphs cannot be generated from the {0} table.'.format(table.title))
        return

    nuke_filter = SpellFilter('Nukes', eq.nukes)
    graph_spells(table, nuke_filter, separate_spells)

    return


def graph_spells(table: parsedb.ParseTable, spell_filter, separate_spells=False):
    """
    Create bar graphs associating cast counts and spells to their respective casters.

    :param table: ParseDB cast table
    :param spell_filter: a typical grouping of spells into heals, utility, or nukes
    :param separate_spells: a flag indicating whether spells should be grouped by type or named individually
    :return: void
    """
    st = pg.style.DarkStyle
    st.font_family = "DeJa Vu Sans"
    st.value_font_size = 8
    chart = pg.StackedBar(style=st, print_values=True, print_zeroes=False)
    chart.show_minor_y_labels = True
    chart.title = '{0}: {1}'.format(table.title, spell_filter.name)
    chart.x_labels = table.column_labels[1:]
    chart.value_formatter = lambda x: '{0:d}'.format(int(x))

    if separate_spells:
        spells = [row for row in table.rows if row[0] in spell_filter.spells.keys()]
        for spell in spells:
            chart.add(spell[0], spell[1:])
    else:
        spell_types = dict()
        for row in table.rows:
            t = spell_filter.spells.get(row[0], '')
            if t:
                spell_types[t] = map(op.add, spell_types.get(t, [0] * len(row[1:])), row[1:])
        for spell_type in sorted(spell_types.keys()):
            chart.add(spell_type, list(spell_types[spell_type]))

    chart.render_to_png('{0}/{1}_{2}.png'.format(os.getcwd(), table.title.lower(), spell_filter.name.lower()))

    return


def generate_class_graphs(table: parsedb.ParseTable):
    """
    Create spell cast graphs for each supported EQ class.

    :param table: ParseDB cast table
    :return: void
    """
    dispatch = {
        'Clerics': [graph_heals, graph_utilities],
        'Druids': [graph_heals, graph_utilities, graph_nukes],
        'Shamans': [graph_heals, graph_utilities]
    }
    for f in dispatch.get(table.title, []):
        f(table)
