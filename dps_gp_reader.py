import sys
import re
import collections
from decimal import *
import pprint
pp = pprint.PrettyPrinter(indent=4, stream=sys.stderr)

class GPCastReader:
    """
    TODO: Class documentation
    """
    def __init__(self, input_path, config_path, blacklist_path):
        self.classes = set()
        self.mob = ''
        self.date = ''

        self.gp_lines = read_raw_parse(input_path)
        self.blacklist = read_blacklist(blacklist_path)
        self.config = init_config(config_path)

        self.caster_dod = self.init_caster_dod()

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
        Extract caster names and spell cast get_info from GamParse forum output.

        :return: a dictionary of dictionaries with format
                 caster_dod[caster] = {'spell_1', count_1}, ..., {'spell_n', count_n}
        """
        caster = 'unknown'
        rk = re.compile(' (?:Rk\. )?(?:X{0,3})(?:IX|IV|V?I{0,3})$')
        gp_header = re.compile('(?P<mob>(?:Combined: )?(?:[\w`,]+ ?)+) on (?P<date>\d{1,2}/\d{1,2}/\d{2,4})')
        name_grabber = re.compile('\[B\](?P<name>\w+) - \d+\[/B\]')
        gp_bullet = '   --- '

        caster_dod = collections.defaultdict(dict)
        for line in self.gp_lines:
            if line.upper().startswith('[B]'):
                caster = self.read_entry_header(gp_header, name_grabber, line)
                if caster == 'unknown':
                    continue
                self.classes.add(self.config[caster]['class'])
            elif line.startswith(gp_bullet):
                if caster == 'unknown':
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

    def read_entry_header(self, gp_header, name_grabber, line):
        """
        Read and extract data from a GamParse dps entry header.

        :param gp_header: regex for parsing the main header of the cast output
        :param name_grabber: regex for parsing the entry headers of the cast output
        :param line: line of the cast output file to be parsed
        :return: the name of the player casting, if applicable, or 'unknown' if not applicable
        """
        player = 'unknown'
        m = gp_header.match(line[3:-4])
        n = name_grabber.match(line)
        if m:
            self.mob = m.group('mob')
            self.date = m.group('date')
            pass
        elif n:
            player = n.group('name')
            try:
                self.classes.add(self.config[player]['class'])
            except KeyError as e:
                if player != 'Total':
                    print('Unrecognized player {0}. Please update your config file.'.format(e))
                    player = 'unknown'
        return player

class GPDPSReader:
    def __init__(self, input_path, game_reader):
        self.classes = set()
        self.game_reader = game_reader
        self.gp_lines = read_raw_parse(input_path)
        self.guild_stats = {}
        self.lone_pets = dict()
        self.aliases = self.game_reader.aliases         # For compatibility
        self.errs = game_reader.errs

        self.mob = 'unknown'
        self.time = 0
        self.sdps = 0
        self.date = 'unknown'

        self.dpser_dod = self.init_dps()

    def get_info(self):
        return { 'mob':  self.mob,
                 'dur':  self.time,
                 'on':   self.date,
                 'sdps': self.sdps }

    def init_dps(self):
        gp_header = re.compile('(?P<mob>(?:Combined: )?(?:[\w`,]+ ?)+) on (?P<date>\d{1,2}/\d{1,2}/\d{2,4}) in (?P<time>\d{1,5})sec')
        name_grabber = re.compile('\[B\](?P<name>\w+)\[/B\]')
        dps_grabber = re.compile('(?P<total>\d+) \@ (?P<sdps>\d+) sdps \((?P<dps>\d+) dps in (?P<time>\d+)s\) \[(?P<pct>\d+(\.\d+)?)%\]')
        gp_bullet = ' --- '

        dpser_dod = collections.defaultdict(dict)
        for line in self.gp_lines:
            if line.upper().startswith('[B]'):
                dps_stats = self.read_entry_header(gp_header, name_grabber, line)
                if dps_stats == None:
                    continue
            if line.startswith(gp_bullet):
                if dps_stats == None:
                    continue
                if line[8:12] == 'DMG:':
                    b = dps_grabber.match(line[17:])
                    stats = {
                                'total' : b.group('total'),
                                'sdps'  : b.group('sdps'),
                                'dps'   : b.group('dps'),
                                'time'  : b.group('time'),
                                'pct'   : b.group('pct')
                            }

                    who = dps_stats['name']
                    if who == 'Total':
                        # Header
                        self.guild_stats = stats
                        self.sdps = stats['sdps']
                        continue
                    elif 'pet' in dps_stats:
                        # Un-associated pet
                        stats['pet'] = dps_stats['pet']
                        self.lone_pets[who] = stats
                    else:
                        # Player character
                        if 'joined' in dps_stats:
                            # Applicant
                            stats['joined'] = dps_stats['joined']
                        stats['group'] = dps_stats['group']
                        stats['gid'] = dps_stats['gid']
                        stats['class'] = dps_stats['class']
                        dpser_dod[who] = stats

        self.coalesce_lone_pets(dpser_dod)
        return dpser_dod

    def read_entry_header(self, gp_header, name_grabber, line):
        """
        Read and extract data from a GamParse dps entry header.

        :param gp_header: regex for parsing the main header of the dps output
        :param name_grabber: regex for parsing the entry headers of the dps output
        :param line: line of the dps output file to be parsed
        :return: the raid-info-object of the player doing the dps, if applicable, else None
        """
        hdr = gp_header.match(line[3:-4])
        dps = name_grabber.match(line)
        if hdr:
            self.mob = hdr.group('mob')
            self.time = int(hdr.group('time'))
            self.date = hdr.group('date')
        elif dps:
            player = dps.group('name')
            if player == 'Total':
                return { 'name' : player }

            info = self.game_reader.raider_info(player)
            if info is None:
                err = 'Unrecognized player {0}. Did you forget to associate a pet with its owner in GamParse? Otherwise, add <pet,owner> to pet-owners list or add to ignore list?'.format(player)
                self.errs.append(err)
                sys.stderr.write(err + '\n')
                return None
            if 'pet' in info:
                err = 'Found unassociated pet {0}'.format(player)
                self.errs.append(err)
                sys.stderr.write(err + '\n')
                self.lone_pets[player] = info
                return info
            if 'ignore' in info:
                return None

            self.classes.add(info['class'])
            return info

        return None

    def get_adps_classes(self, cls):
        return self.game_reader.adps_classes(cls)

    def get_aliases(self):
        return self.game_reader.aliases

    def coalesce_lone_pets(self, raiders):
            """
            Merge all un-associated pet's stats into a players stats.
            """

            for pet in self.lone_pets:
#                pp.pprint(pet)

                owner = self.game_reader.get_pet_owner(pet)
                if owner is None:
                    err = 'oops! Internal error: Unrecognized pet {0}.'.format(pet)
                    self.errs.append(err)
                    sys.stderr.write(err + '\n')
                elif owner not in raiders:
                    err = 'Unrecognized owner {0} for pet {1}. Either pet-owners file is incorrect or raid file is incorrect.'.format(pet, owner)
                    self.errs.append(err)
                    sys.stderr.write(err + '\n')
                else:
                    ostats = raiders[owner]
                    pstats = self.lone_pets[pet]

#                    pp.pprint("BEFORE: (o,p)")
#                    pp.pprint(owner)
#                    pp.pprint(ostats)
#                    pp.pprint(pstats)
#                    pp.pprint(self.guild_stats['total'])

                    getcontext().prec = 12          # (somewhat) arbitrary

                    # 'total', 'sdps', 'dps', 'time', 'pct'

                    t = Decimal(ostats['total']) + Decimal(pstats['total'])
                    ostats['total'] = str(int(t))

                    # edge cases not handled: e.g. owner attack; stop; pet attack
                    if Decimal(ostats['time']) < Decimal(pstats['time']):
                        ostats['time'] = pstats['time']

                    ostats['dps']  = str(int(t / Decimal(ostats['time'])))
                    ostats['sdps'] = str(int(t / Decimal(self.guild_stats['time'])))

                    p  = t / Decimal(self.guild_stats['total'])
                    getcontext().prec = 3
                    ostats['pct']  = str(p * 100)

#                    pp.pprint("AFTER:")
#                    pp.pprint(ostats)

def read_raw_parse(path):
        """
        Read GamParse's forum output into a list.

        :param path: path to the file containing GamParse output
        :return: a list containing the lines of the input file
        """
        with open(path, 'r') as input_handle:
            return input_handle.read().splitlines()
