#!/bin/sh


while getopts p:e:d: opt
do
   case $opt in
       p) pyth=$OPTARG;;
       e) pythscript=$OPTARG;;
       d) direct=$OPTARG;;
	   ?) echo "Usage ($0) -p python_executable -d source_directory -e pythonscript\n";;
   esac
done
logf=$direct/$pythscript.log
script=$direct/$pythscript 

ans=`ps -efww | grep -w $script |grep -v grep|wc -l`

if [ $ans -ge 1 ];
then
echo "Already running"
else
cd $direct
$pyth $script >>$logf 2>&1
fi
