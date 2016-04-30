import csv
import re
import collections


class GPCastReader:
    """
    TODO: Class documentation
    """
    def __init__(self, input_path, config_path, blacklist_path):
        self.classes = set()
        self.gp_lines = self.read_raw_parse(input_path)
        self.config = self.init_config(config_path)
        self.blacklist = self.init_blacklist(blacklist_path)
        self.caster_dod = self.init_caster_dod()

    @staticmethod
    def read_raw_parse(input_path):
        """
        Read GamParse's forum output into a list.

        :param input_path: the location of the file storing GamParse's output
        :return: a list containing the rows of GamParse's forum output
        """
        with open(input_path, 'r') as input_handle:
            return input_handle.read().splitlines()

    @staticmethod
    def init_config(path):
        """
        Read config.txt into a dictionary of dictionaries.

        The file config.txt should be in CSV format with the values name, class, alias.

        :param path: the relative path to the config file
        :return: A dictionary of dictionaries with format cfg[name] = dictionary{'class', 'alias'}
        """
        with open(path, 'r') as cfg_handle:
            cfg_reader = csv.DictReader(cfg_handle, ['name', 'class', 'alias'])
            return {row['name'].strip(): {'class': row['class'].strip(),
                                          'alias': row['alias'].strip()} for row in cfg_reader}

    @staticmethod
    def init_blacklist(path):
        """
        Read the blacklist file into a list of ignored spells.

        :param path: the relative path to the blacklist file
        :return: a list of blacklisted spells
        """
        with open(path, 'r') as bl_handle:
            return bl_handle.read().splitlines()

    def is_blacklisted(self, spell_name):
        """
        Indicate whether a spell is blacklisted or not.

        :param spell_name: the spell to check
        :return: True if spell is ignored, otherwise false.
        """
        return any(spell_name.startswith(b) for b in self.blacklist)

    def get_eq_classes(self):
        """
        Create a set of unique classes from a config dictionary of dictionaries.

        :return: the set of EQ classes found in the config file
        """
        return set([v['class'] for x, v in self.config.items()])

    def get_spells_cast_by_class(self):
        """
        Accumulate unique spells cast per eq class.

        :return: a dictionary with the format class_spells = (spell_1, ..., spell_n)
        """
        class_spells = collections.defaultdict(set)
        for caster, spells in self.caster_dod.items():
            eq_class = self.config[caster]['class']
            class_spells[eq_class].update(set(spells))
        return class_spells

    def init_caster_dod(self):
        """
        Extract caster names and spell cast info from GamParse forum output.

        :return: a dictionary of dictionaries with format caster_dod[caster] = {spell_1, count_1}, ..., {spell_n, count_n}
        """
        caster = 'unknown'
        rk = re.compile(' (?:Rk\. )?(?:X{0,3})(?:IX|IV|V?I{0,3})$')
        gp_header = re.compile('(?:Combined: )?(?:[\w`]+ )+on \d{1,2}/\d{1,2}/\d{2,4}')
        gp_footer = 'Produced by GamParse'
        gp_bullet = '   --- '

        caster_dod = collections.defaultdict(dict)
        for line in self.gp_lines:
            if line.upper().startswith('[B]'):
                if gp_header.match(line[3:-4]) or gp_footer in line:
                    caster = 'unknown'
                    continue
                caster = line[3:-4].split(" - ")[0]
                if caster is 'Firiona Vie':
                    continue
                self.classes.add(self.config[caster]['class'])
            elif line.startswith(gp_bullet):
                if caster is 'Firiona Vie':
                    continue
                scc = line[len(gp_bullet):].split(" - ")
                spell = rk.sub('', scc[0])
                if not self.is_blacklisted(spell):
                    if spell in caster_dod[caster]:
                        print(('Spell {0} already exists in dictionary for {1} with cast count {2}... '
                               'incrementing by {3}').format(spell, caster, caster_dod[caster][spell], scc[1]))
                        caster_dod[caster][spell] = str(int(caster_dod[caster][spell]) + int(scc[1]))
                    else:
                        caster_dod[caster].update({spell: scc[1]})
        return caster_dod
