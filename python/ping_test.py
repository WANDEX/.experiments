#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time

# Google Public DNS: 8.8.8.8 or 8.8.4.4
HOST = "8.8.8.8"
GET_PACKET_LOSS = True

statistic = {'transmitted': 0,
             'received': 0,
             'unreachable': 0}


def packet_loss():
    ''' Calculate packet_loss % '''
    received = statistic.get('received', 0)
    transmitted = statistic.get('transmitted', 0)
    return(round(100 - (received / transmitted * 100), 2))


def update_statistic(key, get_packet_loss=False):
    ''' Update ping statistic '''
    statistic['transmitted'] = statistic.get('transmitted', 0) + 1
    statistic[key] = statistic.get(key, 0) + 1
    if get_packet_loss:
        statistic['packet_loss'] = statistic.setdefault('packet_loss', 0)
        statistic['packet_loss'] = packet_loss()
    return(statistic)


def subping(host_or_ip, interval=4, packetsize=8, get_packet_loss=False):
    ''' Calls system "ping" command as subprocess, and count packets by returncode.
        returncode: "0" - success,
        returncode: "1", "2" - interprets like host unreachable. (see man ping)
    Required parameter:
        host_or_ip (str, address of host/ip to ping)
    Optional parameters:
        interval   (int, wait interval seconds between sending each packet),
        packetsize (int, number of data bytes to be sent + 8 bytes of ICMP
        header data)
    '''
    command = ["ping", str(host_or_ip), "-c", "1", "-s", str(packetsize)]
    try:
        # Popen parameters: discard input, output and error messages
        check = subprocess.Popen(command, bufsize=1,
                                 stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        time.sleep(interval)
        # to get returncode, but don't raise CalledProcessError()
        stdout, _ = check.communicate()
        check.poll()
        if check.returncode == 0:
            return(update_statistic('received', get_packet_loss))
        elif check.returncode == 2:
            return(update_statistic('unreachable', get_packet_loss))
        elif check.returncode == 1:
            # if ping does not receive any reply packets at all. (see man ping)
            return(update_statistic('unreachable', get_packet_loss))
        else:
            print("unhandled returncode {0}".format(str(check.returncode)))
        # check.stdout.close()
    except subprocess.CalledProcessError:
        # suppress the original error, with "from None"
        raise RuntimeError("Something wrong here!") from None


def loop(packets=1):
    ''' Main loop
    Optional parameters:
    packets  (int, number of retries)
    '''
    packet = 0
    while packet < packets:
        packet += 1
        print(subping(HOST, get_packet_loss=GET_PACKET_LOSS))


def by_time():
    pass


loop(10)
