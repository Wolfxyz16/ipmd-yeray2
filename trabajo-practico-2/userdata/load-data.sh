#!/bin/sh

hdfs namenode &

hadoop fs -put /userdata /userdata
hadoop fs -ls /
