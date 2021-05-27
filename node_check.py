#!/usr/bin/python3.8
import sys
import requests
import json
from subprocess import Popen, PIPE
import shlex
import socket


def get_status(api_access_key):
    url = 'https://nodes.presearch.org/api/nodes/status/' + api_access_key
    res = requests.get(url)

    if (res.ok):
        return json.loads(res.content)
    else:
        res.raise_for_status()


def get_ips():
    cmd = shlex.split('/sbin/ip -4 a')
    child = Popen(cmd, stdout=PIPE)
    if child.wait():
        raise Exception("couldn't get ip address")
    print("IP: " + str(child.stdout.read()))

def get_ip():
    cmd = shlex.split('/sbin/ip -4 a')
    child = Popen(cmd, stdout=PIPE)
    if child.wait():
        raise Exception("Couldn't execute ifconfig")

    output = child.stdout.readlines()

    ips = []
    for line in output:
        string = line.decode("utf-8").lstrip().rstrip()
        if string.startswith('inet '):
            ips.append(string.split(" ")[1])

    return ips


def need_restart(json_data):
    for node, node_value in json_data['nodes'].items():
        status = node_value['status']['connected']
        if not status:
            ips = get_ip()
            for ip in ips:
                if ip.startswith(node_value['meta']['remote_addr']):
                    print ( "IP: " + ip + " REMOTE IP RETURNED: " + node_value['meta']['remote_addr'])
                    return True

    return False

def do_restart():
    cmd = shlex.split('docker stop presearch-node')
    print("executing docker stop presearch-node")
    child = Popen(cmd, stdout=PIPE)
    child.wait()

    cmd = shlex.split('docker stop presearch-auto-updater')
    print("executing docker stop presearch-auto-updater")
    child = Popen(cmd, stdout=PIPE)
    child.wait()

    cmd = shlex.split('docker start presearch-auto-updater')
    print("executing docker start presearch-auto-updater")
    child = Popen(cmd, stdout=PIPE)
    if child.wait():
        raise Exception("couldn't get restart presearch-auto-updater")


    cmd = shlex.split('docker start presearch-node')
    print("executing docker start presearch-node")
    child = Popen(cmd, stdout=PIPE)
    if child.wait():
        raise Exception("couldn't get restart preserach-node")


    print("restart success")


if __name__ == '__main__':
    if( len(sys.argv) < 2):
        print("invalid number of arguments")
        sys.exit(1)

    j_data = get_status(sys.argv[1])

    if (need_restart(j_data)):
        do_restart()

    sys.exit(0)
