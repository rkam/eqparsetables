#!/usr/bin/env ruby

require_relative "class_info"

while gets
  puts $_ if EQ_CLASSES_DPS.find_index($_.split(",")[1])
end
