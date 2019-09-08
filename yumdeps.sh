#!/bin/bash

tmp1="/tmp/yumdeps1-`date +%Y%M%d%H%M%S`"
tmp2="/tmp/yumdeps2-`date +%Y%M%d%H%M%S`"
echo $tmp1, $tmp2

yum list | egrep 'gemini-production|gemini-devel|gemini-testing' | awk '{print $1}' > $tmp1

cp /dev/null $tmp2

echo "Building index..."
for pkg in $(cat list); do
    echo $pkg
    yum deplist VDCT 2>/dev/null $pkg>>$tmp2;
done
