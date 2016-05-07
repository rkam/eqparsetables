#!/usr/bin/env ruby

require_relative "class_info"

while gets
  a = $_.split("\t")

  next if a[2] == "50"

  i = EQ_CLASSES_LONG.find_index(a[3])

  print("#{a[1]},#{EQ_CLASSES_SHORT[i]},#{a[1]}\n")
end
