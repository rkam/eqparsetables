#!/usr/bin/env ruby

require_relative "class_info"

$for_apps = false

n = 0
ARGV.each do | a |
  if a[0].chr == '-' then
    case a[1].chr
      when 'a' then $for_apps = !$for_apps
      else puts "Ignoring unknown option '#{a}'"
    end
    n += 1
  end
end

ARGV.shift n

if ARGV.length > 0
  puts "Ignoring extra args '#{ARGV}'"
  ARGV.shift ARGV.length
end

while gets
  a = $_.chomp.split("\t")

  next if a[1] == "50"      # shouldnt happen

  i = EQ_CLASSES_LONG.find_index(a[2])

  if $for_apps                         # Apps or full members
    app_date = a[-1].split(" ")[-1]
    print("#{a[0]},#{EQ_CLASSES_SHORT[i]},#{a[0]},#{app_date}\n")
  else
    print("#{a[0]},#{EQ_CLASSES_SHORT[i]},#{a[0]}\n")
  end

end
