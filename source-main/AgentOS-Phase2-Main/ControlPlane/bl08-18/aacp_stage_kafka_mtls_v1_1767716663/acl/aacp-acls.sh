#!/usr/bin/env bash
# Example ACLs for AACP topics
kafka-acls.sh --bootstrap-server kafka:9093 --command-config client.properties  --add --allow-principal User:CN=aacp-producer  --producer --topic aacp.control.*

kafka-acls.sh --bootstrap-server kafka:9093 --command-config client.properties  --add --allow-principal User:CN=aacp-consumer  --consumer --topic aacp.control.* --group aacp-*
