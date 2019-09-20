#!/bin/csh -f
unalias *

# File names
set tmp_list="/tmp/yumdepsl-`date +%Y%M%d%H%M%S`"
set tmp_info="/tmp/yumdepsi-`date +%Y%M%d%H%M%S`"
set tmp_dep="/tmp/yumdepsd-`date +%Y%M%d%H%M%S`"
set tmp_errors="/tmp/yumdepse-`date +%Y%M%d%H%M%S`"
set out_list = './pkg.list'
set out_info = './pkg.info'
set out_dep = './pkg.dep'
set out_errors = './pkg.errors'
#echo $tmp_info, $tmp_dep

# Get the list of packages
echo "getting package list..."
yum list | egrep 'gemini-production|gemini-devel|gemini-testing' | awk '{print $1}' > $tmp_list

# Get the package information
cp -f /dev/null $tmp_info
echo "getting package info..."
foreach pkg (`cat $tmp_list`)
    (yum info $pkg >> $tmp_info) >& $tmp_errors
end

# Get the package dependencies
cp -f /dev/null $tmp_dep
echo "getting package dependencies..."
foreach pkg (`cat $tmp_list`)
    (yum deplist $pkg >> $tmp_dep) >>& $tmp_errors
end

# Save temporary files
mv -f $tmp_list $out_list
mv -f $tmp_info $out_info
mv -f $tmp_dep $out_dep
if (`wc -l $tmp_errors` == 0) then
    rm -f $tmp_errors
else
    mv -f $tmp_errors $out_errors
endif
