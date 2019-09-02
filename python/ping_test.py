#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from itertools import count
from threading import Thread
from time import sleep

# defaults: Google Public DNS: 8.8.8.8 or 8.8.4.4
HOST = "8.8.8.8"
INTERVAL = 4
PACKETSIZE = 8
GET_PACKET_LOSS = True
TIME_SLICE = 1

time_iteration = count()

statistics = {"transmitted": 0, "received": 0, "unreachable": 0}


def calculate_packet_loss():
    """Calculate packet_loss %."""
    received = statistics.get("received", 0)
    transmitted = statistics.get("transmitted", 0)
    return round(100 - (received / transmitted * 100), 2)


def update_statistics(key, get_packet_loss=GET_PACKET_LOSS):
    """Update ping statistics."""
    statistics["transmitted"] = statistics.get("transmitted", 0) + 1
    statistics[key] = statistics.get(key, 0) + 1
    if get_packet_loss:
        statistics["packet_loss"] = statistics.setdefault("packet_loss", 0)
        statistics["packet_loss"] = calculate_packet_loss()
    return statistics


def return_swith(returncode):
    """Gets returncode from subping() and returns update_statistics().

    Required parameter: returncode.
        returncode: "0" - success,
        returncode: "1", "2" - interprets like host unreachable. (see man ping)
    """
    switch = {
            0: "received",
            1: "unreachable",
            2: "unreachable",
    }
    return update_statistics(switch.get(returncode, None))


def reset_stats(dictionary):
    """Reset to 0 all dictionary values.

    Required parameter:
        dictionary: (dict, dictionary to reset)
    """
    for key in dictionary.keys():
        dictionary[key] = 0
    print("\nValues are now set to 0.\n{0}\n".format(dictionary.items()))


def count_iteration(counter, string=""):
    """Iteration counter for recursive functions and loops.

    Required parameter:
        counter: (itertools.count(), global variable)
    Optional parameter:
        string: (str, optional message after iteration number)
    """
    iteration = next(counter)
    print("{0}:{1} iteration.".format(str(iteration), string))
    return iteration


def subping(
    host_or_ip=HOST,
    interval=INTERVAL,
    packetsize=PACKETSIZE,
    get_packet_loss=GET_PACKET_LOSS,
):
    """Calls system "ping" command as subprocess, and count packets by
    returncode.

        returncode: "0" - success,
        returncode: "1", "2" - interprets like host unreachable. (see man ping)
    Required parameter:
        host_or_ip (str, address of host/ip to ping)
    Optional parameters:
        interval   (int, wait interval seconds between sending each packet),
        packetsize (int, number of data bytes to be sent + 8 bytes of ICMP
        header data)
    """
    command = ["ping", str(host_or_ip), "-c", "1", "-s", str(packetsize)]
    try:
        # Popen parameters: discard input, output and error messages
        ping = subprocess.Popen(
            command,
            bufsize=1,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        sleep(interval)
        # to get returncode, but don't raise CalledProcessError()
        stdout, _ = ping.communicate()
        ping.poll()
        if ping.returncode == 0:
            return update_statistics("received", get_packet_loss)
        elif ping.returncode == 2:
            return update_statistics("unreachable", get_packet_loss)
        elif ping.returncode == 1:
            # if ping does not receive any reply packets at all. (see man ping)
            return update_statistics("unreachable", get_packet_loss)
        else:
            print("unhandled returncode {0}".format(str(ping.returncode)))
            ping.kill()
        # ping.stdout.close()
    except subprocess.CalledProcessError:
        ping.kill()
        # suppress the original error, with "from None"
        raise RuntimeError("Something wrong here!") from None


def ping_loop():
    """Infinite ping_loop."""
    while True:
        print(subping())


def time_loop(time_slice=TIME_SLICE):
    """Infinite time_loop.

    Optional parameters:
        time_slice (int, last 't' minutes to store statistics)
    """
    count_iteration(time_iteration, "time_loop()")
    time_slice *= 60
    while time_slice:
        mins, secs = divmod(time_slice, 60)
        timeformat = "{:02d}:{:02d}".format(mins, secs)
        print(timeformat, end="\r")
        sleep(1)
        time_slice -= 1
    print("Timer Has Ended.")
    reset_stats(statistics)
    time_loop()


if __name__ == "__main__":
    print("Starting...")
    thread_ping = Thread(target=ping_loop, daemon=True)
    thread_time = Thread(target=time_loop, daemon=True)
    thread_ping.start()
    thread_time.start()
    thread_ping.join()
    thread_time.join()
    print("Done.")
