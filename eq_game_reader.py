#!/usr/bin/env python
"""Raid Information pertaining to the Everquest Game"""

import sys
import csv
import re
import collections
import datetime
import eqclasses as eqc

class GameReader:
    """
    A class that reads various data files and contains their pertinent info.
    Properties:  guild - the guild roster
                 raid - the raid roster for this event
                 ignore - the list of mobs/players to ignore
    """
    def __init__(self, config_files):
        """
        Given a list of files, read and retain raid information.

        :param config_files: the list of files describing the raid
            { 'guild'   : the guild_roster at the time of the raid
              'raid'    : the raid_roster the current event
              'ignore'  : the file containing parse entries to ignore
              'pets'    : the file associating pets to their owners
            }
        """
        self.guild   = GuildReader(config_files['guild'])
        self.raid    = RaidReader(config_files['raid'])
        self.ignore  = self.process_ignore_list(config_files['ignore'])
        self.pets    = self.process_pet_list(config_files['pet_owners'])
        self.aliases = process_alias_list(config_files['aliases'])

    ################## End initializers #################

    @staticmethod
    def adps_classes(cls):
        """
        Given a class, return the list of associated ADPS classes

        :param cls: the class
        :return: the list of ADPS classes
        """
        return eqc.adps_classes(cls)

    def get_pet_owner(self, pet):
        """
        Given a pet, return its owner

        :param pet: the name of the pet
        :return: the name of the owner
        """
        return self.pets[pet] if pet in self.pets else None

    def process_ignore_list(self, path):
        """
        Read the mobs-to-ignore file into a list.

        :param path: the path to the ignore file
        :return: a list of ignored mobs
        """
        with open(path, 'r') as fh:
            return fh.read().splitlines()
                 # TODO:  row for row in fh if not row.startswith('#')),

    def process_pet_list(self, path):
        """
        Read the pet_owners file into a list.

        :param path: the path to the pet_owners file
        :return: a dict of { pet : owner }
        """
        with open(path, 'r') as fh:
            reader = csv.DictReader((row for row in fh
                                        if not row.startswith('#')
                                    ),
                    [ 'pet', 'owner' ], delimiter='	')

            return { row['pet'].strip() : row['owner'].strip()
                            for row in reader
                        }

    def raider_info(self, raider):
        """
        Given a raider's name, return extra information on that raider
        if the raider is NOT a member of the guild then
            If that raider should be ignored, the returned list will include a
                key-value of { 'ignore' : True }
            If that raider is recognized as a pet, the returned list will
                include a key-value of { 'pet' : True }
            otherwise, None will be returned

        Otherwise, the raider is a guild member and additional key-value pairs
            will be added, as appropriate:
            'name', 'class',
            'gid' (group #),
            'group' (dict containing group info e.g. class list and groupmate names)
            - if the raider is an applicant:
                'joined' (date member joined),

        :param path: the path to the pet_owners file
        :return: a dict of { name : raider, other_attributes }
        """
        if not raider in self.guild.members:
            if raider in self.ignore:
                return { 'name' : raider, 'ignore' : True  }
            if raider in self.pets:
                return { 'name' : raider, 'pet' : True }
            return None

        g = self.guild.members[raider]
        if raider in self.raid.raiders:
            r = self.raid.raiders[raider]
        else:
            # TODO: need to be more lenient on this - basically, it requires
            # TODO:   a raid dump for each event and then based on parse time
            # TODO:   (which isn't in the parse dump), find the closest raid
            # TODO:   file.  Or allow/specify multiple raid files (raid dir?)
            # TODO: Still doesn't help the char-changed-group cases.
            # TODO:     - so although it's best to have a raid dump per event,
            # TODO:       need to intelligently handle this
            sys.stderr.write(raider + ' not found in raid - wrong raid file?\n')
            r = { 'gid': '0' }

        cls = eqc.map_class_to_short(g['class'])
        info = {
                    'name':      raider,
                    'class':     cls,
                    'highlight': eqc.highlight_for_class(cls),
                    'gid':       r['gid'],
                    'group':     self.raid.groups[r['gid']],
               }
        if 'joined' in g:
            info['joined'] = g['joined'] 
        return info

    def raiders(self):
        """
        Return the list of raiders
        """
        return self.rosters['raid'].raiders
    def groups(self):
        """
        Return the list of groups within the raid
        """
        return self.rosters['raid'].groups

    def possible_raiders(self):
        """
        Return the list of raiders within the guild
        """
        return self.rosters['guild'].full_members
    def applicant_raiders(self):
        """
        Return the list of applicants within the guild
        """
        return self.rosters['guild'].applicants
    def members(self):
        """
        Return the list of all members of the guild (raiders, applicants and
            non-raiders)
        """
        return self.rosters['guild'].members

def process_alias_list(path):
    """
    Read config.txt into a dictionary of dictionaries with format cfg[player] = {'class', 'alias'}

    The config file should be in CSV format with the values name, class, alias.

    :param path: path to the config CSV file
    :return: A dictionary of dictionaries with the format cfg[player_name] = {'class', 'alias'}
    """
    with open(path, 'r') as cfg_handle:
        cfg_reader = csv.DictReader((row for row in cfg_handle if not row.startswith('#')),
                                    ['name', 'class', 'alias'])
        return {row['name'].strip(): {'class': row['class'].strip(),
                                        'alias': row['alias'].strip()} for row in cfg_reader}

class GuildReader:
    """
    A class representing the guild roster pertaining to raids.
        The roster contains all members.  Of those members, some are raiders
            and some are not (regular) raiders.  Of those members, some are
            applying to become a raider.
        Properties of this class are each of those groups:
            (members, full_members (aka raiders), applicants)
        Pertinent info for each list is:
                { name, class, title, comment, last_on }
            Title is one of the property titles.
            Comment is the date joined
            If the member is an applicant, the comment is parsed and the
                field 'joined' contains the date the applicant joined the guild.
    """

    titles = { 'Applicant', "Member (F)", "Alt" }   # All others are full members

    def __init__(self, path):
        self.members      = dict()           # entire roster
        self.full_members = dict()           # current full members
        self.applicants   = dict()           # current applicants
#        self.mia_members  = dict()
#            mia_members is currently unused (160517) but in future will be used
#                to limit the size of the list (optimization) based on
#                when the user last logged on (last_on field)..

        # File format changed on 160512
#        if path =~ /RaidRoster-20160512-/ :
#            keys = [ 'name', 'level', 'class', 'title', 'location', 'last_on', 'unknown', 'comment' ] # others ...
#        else:
        keys = [ 'name', 'level', 'class', 'title', 'location', 'last_on', 'unknown', 'comment' ] # others ...

        with open(path, 'r') as fh:
            reader = csv.DictReader((row for row in fh if not row.startswith('#')),
                             keys, delimiter='	')

            self.members = {
                            row['name'].strip(): {
                                'class': row['class'].strip(),
                                'title': row['title'].strip(),
                                'comment': row['comment'].strip(),
                                'last_on': row['last_on'].strip(),
                            } for row in reader
                           }

        # TODO: they can't be in raid if they haven't been on in a while
        # TODO: HOWEVER, that requires a new roster dump every raid day:
#        self.members = { row for row in members if row['last_on'] is 'today' }
#        self.members = { row for row in members if row['last_on'] is 'in the last month' }

        join_grabber = re.compile('.*Tagged (?P<mo>\d{1,2})/(?P<dy>\d{1,2})/(?P<yr>\d{2,4}).*')

        ##TODO MAYBE: could just add joined date only for applicants and then
        ##TODO          generate applicant list if needed (i.e. no parallel lists)
        for name, attr in self.members.items():
            if attr['title'] == 'Applicant':
                n = join_grabber.match(attr['comment'])
                if n:
                    attr['joined'] = datetime.datetime(int(n.group('yr')), int(n.group('mo')), int(n.group('dy')))
                else:
                    sys.stderr.write('No join date for applicant {0}.\n'.format(name))
                self.applicants[name] = attr
            elif attr[ 'title'] not in GuildReader.titles:
                self.full_members[name] = attr

class RaidReader:
    """
    A class representing the raid roster.
        The roster contains all raiders and the group make-up of the raid.
        The raider list is indexed by name and contains a list of { class, gid }
            where gid is the group number (1..12, and 0 for no group)
        The groups list is indexed by group number and contains a list of
            { name, class } pairs.
    """
    def __init__(self, path):
        self.raiders      = dict()           # indexed by name
        self.groups       = { 0: [] }        # indexed by group number

        # File format changed on 160512
#        if path =~ /RaidRoster-20160512-/ :
#            keys = [ 'gid', 'name', 'level', 'class', 'role' ] # others ...
#        else:
        keys = [ 'gid', 'name', 'level', 'class', 'role' ] # others ...

        with open(path, 'r') as fh:
            reader = csv.DictReader((row for row in fh if not row.startswith('#')),
                            keys, delimiter='	')

            for row in reader:
                nam = row['name'].strip()
                cls = eqc.map_class_to_short(row['class'].strip())
                gid = row['gid'].strip()

                if not nam in self.raiders: self.raiders[nam] = []
                if not gid in self.groups:  self.groups[gid] = []

                self.raiders[nam] =     { 'class': cls,  'gid': gid }
                self.groups[gid].append({ 'class': cls, 'name': nam })

        # group	   char	       level	class	role	        other
        # 1	Kelliene	105	Druid	Raid Leader	

