#!/usr/bin/env ruby

#require "awesome_print"

require_relative "class_info"

#  12  Chalupabatman 105 Berserker
#  12  Cilenne 105 Bard
#  12  Jazrakhan 105 Shaman
#  12  Kazden  105 Rogue
#  12  Kraythos  105 Ranger
#  12  Lomixx  105 Beastlord Group Leader
# ==>
#   12	__char__,BER,BRD,SHA,ROG,RNG,BST	Chalupabatman,Cilenne,Jazrakhan,Kazden,Kraythos,Lomixx
#     where __char__ would be each of the members

groups = {}

while gets
  a = $_.chomp.split("\t")
  next unless a.length > 0

  next if a[2] == "50"

  gid = a[0].to_i
  name = a[1]
  cls = EQ_CLASSES_SHORT[EQ_CLASSES_LONG.find_index(a[3])]

  groups[gid] ||= {}
  groups[gid]['classes'] ||= []
  groups[gid]['members'] ||= []

  groups[gid]['classes'].push cls
  groups[gid]['members'].push name

end

groups.each { |g|
  data = g[1]

  gid = g[0]
  ml = data['members']
  m = ml.join(',')
  c = data['classes'].join(',')

  ml.each { |n|
    puts "#{n}\t#{gid}\t#{c}\t#{m}"
  }
}
