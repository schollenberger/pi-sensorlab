#!/bin/sh
#
pat="$1"
repl="$2"

echo "Replace the substring <$pat> with <$repl> in all files that match first substring."
echo "Press key to continue..."
read line
echo
find . -name "*${pat}*" > _xx1.tmp
echo "Matching files"
echo
cat _xx1.tmp
echo "Press key to continue..."
read line
cat _xx1.tmp | sed "s/$pat/$repl/" > _xx2.tmp
paste _xx1.tmp _xx2.tmp | xargs -n 2
echo
echo "Does this look right ?"
echo "Press key to continue..."
read line
paste _xx1.tmp _xx2.tmp | xargs -n 2 mv
echo
echo "Files renamed."
rm _xx1.tmp _xx2.tmp
echo "That's all..."

