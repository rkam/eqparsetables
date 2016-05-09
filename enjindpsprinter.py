import operator
import collections
import sqlite3
import sys
import everquestinfo as eq

# NOTE: different spacing in this file to accomodate the print ruler

class EnjinDPSPrinter:
  def __init__(self, reader):
    self.dps_entries = reader.dps_entries
    self.event       = reader.event

  def print_all_tables(self, add_columns):
    """Print all parsed class tables in enjin forum table format.

    :rtype: none
    """

    print("\n" + self.event + "\n")
    #               1         2         3         4         5         6
    #      12345678901234567890123456789012345678901234567890123456789012345
    #      123456789012345 123456789012 1234567890 1234567890 1234 1234
    print("         Player      Damage      DPS        SDPS   Time  PCT")
    #        Chalupabatman ___588397540 ___6763190 ___6763190 __87 _100

    first = True
    for data in self.dps_entries:
      sys.stdout.write('%15s %12s %10s %10s %4s %4s' % (
                              data['name'], data['total'], data['dps'],
                              data['sdps'], data['time'], data['pct']
                              ))
      if 'class' in add_columns and 'class' in data:
        sys.stdout.write(' %4s' % (data['class']))
      if 'groupID' in add_columns and 'gID' in data:
        sys.stdout.write(' %4s' % (data['gID']))
      if 'groupClasses' in add_columns and 'gClasses' in data:
        sys.stdout.write(' %23s' % (data['gClasses']))  # 6 * 4 - 1
#      if 'groupMembers' in add_columns and 'gMembers' in data:
#        sys.stdout.write(' %239s' % (data['gMembers']))  # 6 * 20 - 1

      sys.stdout.write("\n")

      if first:
        print("")
        first = False

  def print_class_table(self, eq_class):
    """Print the parse table of a single class

    :param eq_class: The EQ abbreviation of the class to be printed
    :return: none
    """

# vim:ts=2:sw=2:sts=2:et:colorcolumn=80
