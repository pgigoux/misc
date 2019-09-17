#!/bin/csh -f
unalias *

# File names
set tmp1="/tmp/yumdeps1-`date +%Y%M%d%H%M%S`"
set tmp2="/tmp/yumdeps2-`date +%Y%M%d%H%M%S`"
set info = './pkg.info'
set dep = './pkg.dep'
set errors = './pkg.errors'
#echo $tmp1, $tmp2

yum list | egrep 'gemini-production|gemini-devel|gemini-testing' | awk '{print $1}' > $tmp1

rm -f $errors

cp -f /dev/null $tmp2
echo "getting package info..."
foreach pkg (`cat $tmp1`)
    (yum info $pkg >> $tmp2) >& $errors
end
mv -f $tmp2 $info

cp -f /dev/null $tmp2
echo "getting package dependencies..."
foreach pkg (`cat $tmp1`)
    (yum deplist $pkg >> $tmp2) >>& $errors
end
mv -f $tmp2 $dep

rm -f $tmp1 $tmp2
