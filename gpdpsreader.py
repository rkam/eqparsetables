import sys
import csv
import re
import collections

SKIP_MISSING_PLAYERS_FOR_NOW = True

# [B]DMG:[/B] 588397540 @ 6763190 sdps (6763190 dps in 87s) [100%]
MAIN_DPS_LINE_TOTAL_POS         = 1
MAIN_DPS_LINE_DPS_POS           = 3
MAIN_DPS_LINE_SDPS_POS          = 5     # starts with (
MAIN_DPS_LINE_TIME_ATK_POS      = 8     # ends   with s)
MAIN_DPS_LINE_PCT_TOTAL_POS     = 9     # [x.yy%]

def write_err(s): sys.stderr.write(s)
def write_out(s): sys.stdout.write(s)

class GPDPSReader:
    """
    TODO: Class documentation

    Sample Input:
    [B]Grummus on 5/1/2016 in 87sec[/B]

    [B]Total[/B]
     --- [B]DMG:[/B] 588397540 @ 6763190 sdps (6763190 dps in 87s) [100%]
      --- [B]DMG to PC:[/B] 3763775 @47047dps

    [B]Chalupabatman[/B]
       --- [B]DMG:[/B] 45930481 @ 527937 sdps (588852 dps in 78s) [7.81%]
       # <other rows python-like indenting>

    # ... last entry repeated

    Special: 2: Infusion  6: Staunch 7: Intensity 9: Armor G: Glyph M: Secrets K: Kiss X: Slain $: Saved by DI
    [B]Produced by GamParse v1.5.1.7[/B]

    EOF

    (Currently only) interested in the pair of lines of the form:
        [B]Chalupabatman[/B]
        --- [B]DMG:[/B] 588397540 @ 6763190 sdps (6763190 dps in 87s) [100%]

    """
    def __init__(self, input_path, config_files):
        self.classes     = set()
        self.missing     = []
        self.ignored     = []
        self.event       = ""
        self.gp_lines    = self.read_raw_parse(input_path)

        self.init_configs(config_files)

        self.dps_entries = self.init_dps_entries()

    def dump_missing(self):
        if not self.missing and not self.ignored:
            return

        if self.missing:
            write_err("Players missing from config file:\n")
            for char_name in self.missing:
                write_err("\t{0}\n".format(char_name))

#        if self.ignored:
#            write_err("\nIgnored (blacklisted) mobs:\n")
#            for mob in self.ignored:
#                v_write("\t{0}\n".format(mob))

        write_err("\n")

    @staticmethod
    def read_raw_parse(input_path):
        """
        Read GamParse's forum output into a list.

        :param input_path: the location of the file storing GamParse's output
        :return: a list containing the rows of GamParse's forum output
        """
        with open(input_path, 'r') as input_handle:
            return input_handle.read().splitlines()

    def init_configs(self, paths):
        """
        Read each config file into appropriate dictionary of dictionaries within self.

        The file config.txt should be in CSV format with the values name, class, alias.

        :param paths: the set of relative paths to the config files
        :return: nothing
        """

        self.apps = self.init_config(paths['apps'])

        self.config = self.init_config(paths['members'])      # includes F&F
        self.config.update(self.apps)                         # makes a copy
        self.config.update(self.init_config(paths['others'])) # guests, ex-RA

        self.blacklist = self.init_blacklist(paths['blacklist'])

    @staticmethod
    def init_config(path):
        """
        Read config.txt into a dictionary of dictionaries.

        The file config.txt should be in CSV format with the values name, class, alias.

        :param path: the relative path to the config file
        :return: A dictionary of dictionaries with format cfg[name] = dictionary{'class', 'alias'}
        """
        with open(path, 'r') as cfg_handle:
            cfg_reader = csv.DictReader((row for row in cfg_handle if not row.startswith('#')),
                                        ['name', 'class', 'alias', 'extra'])
            return {
                        row['name'].strip(): {
                            'class': row['class'].strip(),
                            'alias': row['alias'].strip(),
                            'extra': row['extra']
                        }
                        for row in cfg_reader
                    }

    @staticmethod
    def init_blacklist(path):
        """
        Read the blacklist file into a list of ignored spells.

        :param path: the relative path to the blacklist file
        :return: a list of blacklisted spells
        """
        with open(path, 'r') as bl_handle:
            return bl_handle.read().splitlines()

    def is_blacklisted(self, char_name):
        """
        Indicate whether a char_name is blacklisted or not.

        :return: True if character is to be ignored, otherwise false.
        """
        return any(char_name.startswith(b) for b in self.blacklist)

    def get_eq_classes(self):
        """
        Create a set of unique classes from a config dictionary of dictionaries.

        :return: the set of EQ classes found in the config file
        """
        return set([v['class'] for x, v in self.config.items()])

    def init_dps_entries(self):
        """
        Extract character names and dps info from GamParse forum output.

        :return: a dictionary of dictionaries with format dps_entries[char_name] = {spell_1, count_1}, ..., {spell_n, count_n}
        """
        char_name = 'unknown'
        gp_header = re.compile('(?:Combined: )?(?:[\w`]+ )+on \d{1,2}/\d{1,2}/\d{2,4}')
        gp_footer = 'Produced by GamParse'
        gp_keys = '$: Saved by DI'
        gp_bullet = ' --- '

        # Y Header
        # y Total
        # Y     DPS         DATA
        # -     DMG to PC   DATA
        # y Melee Name ...
        # Y     DPS         DATA
        # -     Melee Breakdown Name ...            # Melee, their pet, their swarm pets
        # -         Total,Slash, etc.               DATA
        # -         Normal, Crit, Crippling         DATA
        # -         Attempts, Hits, Misses, etc.    DATA
        #
        # Y = handled, - = not yet

        dps_entries = []
        skip_to_blank_line = False
        for line in self.gp_lines:

            if skip_to_blank_line:
                if line != "":
                    continue
                skip_to_blank_line = False
                continue

            if gp_keys in line:
                continue

            ####################################################################
            # Top level line:   Header, Total DPS, Melee
            if line.upper().startswith('[B]'):
                if gp_header.match(line[3:-4]):
                    self.event = line[3:-4]
                    continue

                if gp_footer in line:
                    self.dump_missing()
                    continue

                char_name = line[3:-4].split(" - ")[0]
                if char_name is 'Firiona Vie':
                    skip_to_blank_line = True
                    continue
                if self.is_blacklisted(char_name):
                    self.ignored.append(char_name)
                    skip_to_blank_line = True
                    continue

                if SKIP_MISSING_PLAYERS_FOR_NOW:
                    if char_name in self.config:
                        self.classes.add(self.config[char_name]['class'])
                    else:
                        self.missing.append(char_name)
                        skip_to_blank_line = True
                else:
                    # includes 'Total'
                    self.classes.add(self.config[char_name]['class'])
            ####################################################################
            # char_name dmg data
            elif line.startswith(gp_bullet):

                skip_to_blank_line = True

                if char_name is 'Firiona Vie':
                    continue
                # [B]DMG:[/B] 45930481 @ 527937 sdps (588852 dps in 78s) [7.81%]

                scc = line[len(gp_bullet):].split(" ")

                dps_entries.append({
                        'name':  char_name,
                        'class': self.config[char_name]['class'],
                        'total': scc[MAIN_DPS_LINE_TOTAL_POS],
                        'dps':   scc[MAIN_DPS_LINE_DPS_POS],
                        'sdps':  scc[MAIN_DPS_LINE_SDPS_POS][1:],
                        'time':  scc[MAIN_DPS_LINE_TIME_ATK_POS][:-2],
                        'pct':   scc[MAIN_DPS_LINE_PCT_TOTAL_POS][1:-2],
                    })

        return dps_entries
