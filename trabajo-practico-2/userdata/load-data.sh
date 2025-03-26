#!/bin/sh

hdfs namenode &

sleep 10

hadoop fs -put /userdata /userdata
hadoop fs -ls /
