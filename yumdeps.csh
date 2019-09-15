#!/bin/csh -f
unalias *


set tmp1="/tmp/yumdeps1-`date +%Y%M%d%H%M%S`"
set tmp2="/tmp/yumdeps2-`date +%Y%M%d%H%M%S`"
set output = './deplist'
#echo $tmp1, $tmp2

yum list | egrep 'gemini-production|gemini-devel|gemini-testing' | awk '{print $1}' > $tmp1

cp /dev/null $tmp2

foreach pkg (`cat $tmp1`)
    #yum deplist VDCT 2>/dev/null $pkg>>log;
    (yum deplist $pkg >> $tmp2) >& errors
end

mv $tmp2 $output

rm -f $tmp1 $tmp2
