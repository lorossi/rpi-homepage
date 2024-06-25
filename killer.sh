#!/bin/bash

# stop the script
for file in *.py
do
    # Get the PID of the process
    pid=$(pgrep -f $file)
    if [ ! -z $pid ]
    then
        # Kill the process
        echo -e "$file has PID: $pid. Killing it..."
        kill $pid
    else
        # If the process is not running, print a message
        echo -e "file is not running."
    fi
done
