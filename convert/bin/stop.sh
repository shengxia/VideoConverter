#!/usr/bin/env bash
#
#/**
# * License placeholder.
# */
#

bin=`dirname "$0"`
bin=`cd "$bin"; pwd`
ROOT=`cd "${bin}/.."; pwd`
SERVICE=videoserver

# create log directory
LogDir="${ROOT}/logs"
mkdir -p "$LogDir"

stdout=${LogDir}/stdout
pid=${LogDir}/pid


if [ -f $pid ]; then
  if ps -p `cat $pid` > /dev/null 2>&1; then	
	  kill -9 `cat $pid` > /dev/null 2>&1;	
	  rm $pid
  fi  
else
  echo $SERVICE not start.
fi
echo $SERVICE have stop.
