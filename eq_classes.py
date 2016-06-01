"""Various information about Everquest Classes"""

"""
List of all classes (short names)
"""
all_classes = {
            "BRD",
            "BST",
            "BER",
            "CLR",
            "DRU",
            "ENC",
            "MAG",
            "MNK",
            "NEC",
            "PAL",
            "RNG",
            "ROG",
            "SHD",
            "SHA",
            "WAR",
            "WIZ",
            }

"""
Map long class names in to short names
"""
map_name = {
            "Bard"           : "BRD",
            "Beastlord"      : "BST",
            "Berserker"      : "BER",
            "Cleric"         : "CLR",
            "Druid"          : "DRU",
            "Enchanter"      : "ENC",
            "Magician"       : "MAG",
            "Monk"           : "MNK",
            "Necromancer"    : "NEC",
            "Paladin"        : "PAL",
            "Ranger"         : "RNG",
            "Rogue"          : "ROG",
            "Shadow Knight"  : "SHD",
            "Shaman"         : "SHA",
            "Warrior"        : "WAR",
            "Wizard"         : "WIZ",
            }

"""
Highlights associated with classes (a different color per class (short name))
"""
map_hl = {
            "BRD" : "#f3efb1",      # light yellow
            "BST" : "#f3efb1",
            "BER" : "#f3efb1",
            "CLR" : "#f3efb1",
            "DRU" : "#f3efb1",
            "ENC" : "#f3efb1",
            "MAG" : "#f3efb1",
            "MNK" : "#f3efb1",
            "NEC" : "#f3efb1",
            "PAL" : "#f3efb1",
            "RNG" : "#f3efb1",
            "ROG" : "#f3efb1",
            "SHD" : "#f3efb1",
            "SHA" : "#f3efb1",
            "WAR" : "#f3efb1",
            "WIZ" : "#f3efb1",
            }
"""
List of DPS classes
"""
dps_all    = frozenset([ "BRD", "BST", "BER", "ENC", "MAG",
                         "MNK", "NEC", "RNG", "ROG", "WIZ" ])

dps_melee  = frozenset([ "BRD", "BST", "BER",
                         "MNK",        "RNG", "ROG",       ])

dps_caster = frozenset(dps_all - dps_melee)

dps_non    = frozenset(all_classes - dps_all)

"""
List of Healer classes
"""
healers = frozenset([ "CLR", "DRU", "PAL", "SHA", ])

"""
List of Tank classes
"""
tanks   = frozenset([ "PAL", "RNG", "SHD", "WAR", ])

"""
Type, if any, of ADPS associated with a class (short name)
There are two types of ADPS: melee_adps, caster_adps (and No ADPS)
NOTE: this is "usual" ADPS classes that would be in a group
       e.g a BRD can be melee or caster ADPS, but is rarely in caster ADPS role.

TODO: expand to be full support (e.g. bards are melee AND caster adps)
"""
map_adps_type = {
            "BRD" : "melee_adps",
            "BST" : "melee_adps",
            "BER" : "melee_adps",
            "CLR" : 'none',
            "DRU" : 'none',
            "ENC" : "caster_adps",
            "MAG" : "caster_adps",
            "MNK" : "melee_adps",
            "NEC" : "caster_adps",
            "PAL" : 'none',
            "RNG" : "melee_adps",
            "ROG" : "melee_adps",
            "SHD" : 'none',
            "SHA" : 'none',
            "WAR" : 'none',
            "WIZ" : "caster_adps"
        }

"""
Map class to "typical" group type, for purposes of DPS parses
"""
dps_group_type = {
            "BRD" : "melee",
            "BST" : "melee",
            "BER" : "melee",
            "CLR" : "caster",
            "DRU" : "caster",
            "ENC" : "caster",
            "MAG" : "caster",
            "MNK" : "melee",
            "NEC" : "caster",
            "PAL" : "tank",
            "RNG" : "melee",
            "ROG" : "melee",
            "SHD" : "tank",
            "SHA" : "melee",
            "WAR" : "tank",
            "WIZ" : "caster",
            }

"""
For each type of ADPS, return the "normal" ADPS classes expected in the group.

TODO: change this to, instead of being "normal" adps per group, to possible
        ADPS per group and then mark differences from the subset
        e.g.   if a melee group has BRD, BST, RNG, SHA, then mark those that
                    are NOT that.  But, if no group has that, but a group
                    has BRD, RNG, SHA, then mark groups that are NOT that.
               also, for casters, ENC vs. ENC + BRD vs. BRD
"""
adps = {
    'melee_adps'  : frozenset([ 'BRD', 'BST', 'RNG', 'SHA' ]),
    'caster_adps' : frozenset([ 'ENC' ]),
    'none'        : frozenset()
}

dpsx = {
    'melee'  : dps_melee,
    'caster' : dps_caster,
    'tank'   : frozenset()
}

"""
Given the full class name (found in parse, guild, raid input files), return
    the short name (used internally and in output).
"""
def map_class_to_short(full):   return map_name[full]

"""
Given a class, return the highlight for that class.
    - Takes either a long or short class name.
"""
def highlight_for_class(cls):
    if cls in map_hl:
        return map_hl[cls]
    c = map_class_to_short(cls)
    if cls in map_hl:
        return map_hl[c]
    return None

"""
GIven a class, return the adps classes associated with it.
"""
def adps_classes(cls):    return adps[map_adps_type[cls]]

"""
GIven a class, return the dps classes associated with it.
"""
def dps_classes(cls):    return dpsx[dps_group_type[cls]]

