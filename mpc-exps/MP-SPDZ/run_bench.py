#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file is taken from https://extgit.iaik.tugraz.at/krypto/hydra/-/blob/master/MP-SPDZ/run_bench.py?ref_type=heads (commit: ff1957ef)
and updated for our benchmark purposes.
"""

from subprocess import Popen, PIPE, STDOUT
import click
from os import getcwd
from datetime import datetime as time

import pandas as pd

#prime is updated to pallas prime
PRIME = "28948022309329048855892746252171976963363056481941560715954676764349967630337"
TIMEOUT = None
COMPILE = "./compile.py"
RUN = "./mascot-party.x"
PROGRAM_PATH = "Programs/my_Programs/"

IP = "127.0.0.1" # Localhost

PORT = "8080"
HOST_FILE = "HOSTS"

VERBOSE = False

print("#####running non verbose#####")

#columns for result_file
cols = "program,using squares,squares,integer triples,vm rounds,rate,input_len,output_len,parties,global data,party 0 runtime,party 1 runtime,party 2 runtime,party 3 runtime,party 4 runtime,party 5 runtime,party 6 runtime,party 7 runtime,party 8 runtime,party 9 runtime,party 10 runtime,party 11 runtime,party 12 runtime,party 13 runtime,party 14 runtime,party 15 runtime,party 16 runtime,party 17 runtime,party 18 runtime,party 19 runtime,party 0 data,party 1 data,party 2 data,party 3 data,party 4 data,party 5 data,party 6 data,party 7 data,party 8 data,party 9 data,party 10 data,party 11 data,party 12 data,party 13 data,party 14 data,party 15 data,party 16 data,party 17 data,party 18 data,party 19 data,party 0 rounds,party 1 rounds,party 2 rounds,party 3 rounds,party 4 rounds,party 5 rounds,party 6 rounds,party 7 rounds,party 8 rounds,party 9 rounds,party 10 rounds,party 11 rounds,party 12 rounds,party 13 rounds,party 14 rounds,party 15 rounds,party 16 rounds,party 17 rounds,party 18 rounds,party 19 rounds,party 0 integer multiplications,party 1 integer multiplications,party 2 integer multiplications,party 3 integer multiplications,party 4 integer multiplications,party 5 integer multiplications,party 6 integer multiplications,party 7 integer multiplications,party 8 integer multiplications,party 9 integer multiplications,party 10 integer multiplications,party 11 integer multiplications,party 12 integer multiplications,party 13 integer multiplications,party 14 integer multiplications,party 15 integer multiplications,party 16 integer multiplications,party 17 integer multiplications,party 18 integer multiplications,party 19 integer multiplications,party 0 integer openings,party 1 integer openings,party 2 integer openings,party 3 integer openings,party 4 integer openings,party 5 integer openings,party 6 integer openings,party 7 integer openings,party 8 integer openings,party 9 integer openings,party 10 integer openings,party 11 integer openings,party 12 integer openings,party 13 integer openings,party 14 integer openings,party 15 integer openings,party 16 integer openings,party 17 integer openings,party 18 integer openings,party 19 integer openings,party 0 triples,party 1 triples,party 2 triples,party 3 triples,party 4 triples,party 5 triples,party 6 triples,party 7 triples,party 8 triples,party 9 triples,party 10 triples,party 11 triples,party 12 triples,party 13 triples,party 14 triples,party 15 triples,party 16 triples,party 17 triples,party 18 triples,party 19 triples,party 0 cpu time,party 1 cpu time,party 2 cpu time,party 3 cpu time,party 4 cpu time,party 5 cpu time,party 6 cpu time,party 7 cpu time,party 8 cpu time,party 9 cpu time,party 10 cpu time,party 11 cpu time,party 12 cpu time,party 13 cpu time,party 14 cpu time,party 15 cpu time,party 16 cpu time,party 17 cpu time,party 18 cpu time,party 19 cpu time"
cols = cols.split(",")

PROGRAMS = [
    "poseidon-2-0-encrypt",
    "poseidon-2-0-hash",
    "hydra-encrypt",
    "hydra-hash"
]



SQUARE_PROGRAMS = [
    "hydra-encrypt",
    "hydra-hash"
]


RUNS =  20

result_file = "result_file.csv"

def find_index(string, find_string, start_index = 0):
  index = string.find(find_string, start_index)
  return index

def parse_line_before(string, find_string):
    index = find_index(string, find_string, 0)
    if index == -1:
        return index
    index_post = index
    while index >= 0:
        if string[index] == "\n":
            break
        index = index - 1
    if index == -1:
        return index
    output = string[index:index_post].strip()
    return output

def parse(file_out, prefix, postfix, start_index):
  index1 = find_index(file_out, prefix, start_index)
  index2 = find_index(file_out, postfix, index1 + 1)
  #print(index1, index2, start_index, prefix, postfix,  file_out)
  if index1 == -1 or index2 == - 1:
      #print(index1, index2, start_index, prefix, postfix,  file_out)
      return -1
  output = file_out[index1 + len(prefix):index2]
  return output

def print_triples(output):
    prefix = "Expected:\n"
    postfix = " inverses"
    inverses = int(parse(output, prefix, postfix, 0))
    if inverses == -1:
        inverses = 0

    prefix = "inverses\n  "
    postfix = " squares"
    squares = int(parse(output, prefix, postfix, 0))
    if squares == -1:
        squares = 0

    prefix = "squares\n  "
    postfix = " muls"
    triples = int(parse(output, prefix, postfix, 0))
    if triples == -1:
        triples = 0

    prefix = "muls\n  "
    postfix = " depth"
    rounds = int(parse(output, prefix, postfix, 0))
    if rounds == -1:
        rounds = 0
    return squares, triples, inverses, rounds

def stats(output):
    prefix = "Time1 = "
    postfix = " seconds"
    time = parse(output, prefix, postfix, 0)
    if time == -1:
        print("    Time parsing Error")
        return False

    prefix = "Data sent = "
    postfix = " MB in "
    data = parse(output, prefix, postfix, 0)
    if data == -1:
        print("    Data parsing Error")
        return False

    prefix = "Global data sent = "
    postfix = " MB (all parties)"
    glob_data = parse(output, prefix, postfix, 0)
    if glob_data == -1:
        print("    Global data parsing Error")
        return False
    
    prefix = "MB in ~"
    postfix = " rounds"
    rounds = parse(output, prefix, postfix, 0)
    if rounds == -1:
        print("    Rounds parsing Error")
        return False

    #detailed costs
    prefix = "Detailed costs:\n"
    postfix = " integer multiplication"
    integer_multiplications = parse(output, prefix, postfix, 0)
    integer_multiplications = str.lstrip(integer_multiplications)
    if integer_multiplications == -1:
        print(output)
        print("    integer_multiplications parsing Error")
        return False
    
    prefix = "integer multiplications\n"
    postfix = " integer openings"
    integer_openings = parse(output, prefix, postfix, 0)
    integer_openings = str.lstrip(integer_openings)
    if integer_openings == -1:
        print("    integer_openings parsing Error")
        return False
    
    prefix = "Spent"
    postfix = "on the online phase"
    online_info = parse(output, prefix, postfix, 0)
    if online_info == -1:
        print("    online_info parsing Error")
        return False
    
    prefix = " "
    postfix = " seconds"
    online_seconds = parse(online_info, prefix, postfix, 0)
    if online_seconds == -1:
        print("    online_seconds parsing Error")
        return False

    prefix = "("
    postfix = " MB"
    data_online = parse(online_info, prefix, postfix, 0)
    if data_online == -1:
        print("    data_online parsing Error")
        return False
    
    prefix = ", "
    postfix = " rounds"
    online_rounds = parse(online_info, prefix, postfix, 0)
    if online_rounds == -1:
        print("    online_rounds parsing Error")
        return False

    prefix = "Spent"
    postfix = "offline phase"
    online_offline_info = parse(output, prefix, postfix, 0)
    if online_offline_info == -1:
        print("    online_offline_info parsing Error")
        return False
    
    prefix = "and"
    postfix = "on the"
    offline_info = parse(online_offline_info, prefix, postfix, 0)
    if offline_info == -1:
        print(online_offline_info)
        print("    offline_info parsing Error")
        return False
    
    prefix = " "
    postfix = " seconds"
    offline_seconds = parse(offline_info, prefix, postfix, 0)
    if offline_seconds == -1:
        print(offline_info)
        print("    offline_seconds parsing Error")
        return False

    prefix = "("
    postfix = " MB"
    data_offline = parse(offline_info, prefix, postfix, 0)
    if data_offline == -1:
        print("    data_offline parsing Error")
        return False
    
    prefix = ", "
    postfix = " rounds"
    offline_rounds = parse(offline_info, prefix, postfix, 0)
    if offline_rounds == -1:
        print("    offline_rounds parsing Error")
        return False

    prefix = "Type int\n"
    postfix = "Triples"
    triples = parse(output, prefix, postfix, 0)
    triples = str.lstrip(triples)
    triples = str.rstrip(triples)
    if triples == -1:
        print("    triples parsing Error")
        return False

  
    prefix = "CPU time = "
    postfix = "\n"
    cpu_time = parse(output, prefix, postfix, 0)
    if cpu_time == -1:
        print("    cpu_time parsing Error")
        return False  

    #Communication details
    prefix = "Broadcasting"
    postfix = "\n"
    broadcasting_info = parse(output, prefix, postfix, 0)
    if broadcasting_info == -1:
        print("    broadcasting_info parsing Error")
        return False
    
    prefix = "taking "
    postfix = " seconds"
    broadcasting_seconds = parse(broadcasting_info, prefix, postfix, 0)
    if broadcasting_seconds == -1:
        print("    broadcasting_seconds parsing Error")
        return False

    prefix = " "
    postfix = " MB"
    broadcasting_data = parse(broadcasting_info, prefix, postfix, 0)
    if broadcasting_data == -1:
        print("    broadcasting_data parsing Error")
        return False
    
    prefix = "in "
    postfix = " rounds"
    broadcasting_rounds = parse(broadcasting_info, prefix, postfix, 0)
    if broadcasting_rounds == -1:
        print("    broadcasting_rounds parsing Error")
        return False

    prefix = "Exchanging one-to-one"
    postfix = "\n"
    exchanging_info = parse(output, prefix, postfix, 0)
    if exchanging_info == -1:
        print("    exchanging_info parsing Error")
        return False
    
    prefix = "taking "
    postfix = " seconds"
    exchanging_seconds = parse(exchanging_info, prefix, postfix, 0)
    if exchanging_seconds == -1:
        print("    exchanging_seconds parsing Error")
        return False

    prefix = " "
    postfix = " MB"
    exchanging_data = parse(exchanging_info, prefix, postfix, 0)
    if exchanging_data == -1:
        print("    exchanging_data parsing Error")
        return False
    
    prefix = "in "
    postfix = " rounds"
    exchanging_rounds = parse(exchanging_info, prefix, postfix, 0)
    if exchanging_rounds == -1:
        print("    exchanging_rounds parsing Error")
        return False
    
    prefix = "Receiving directly"
    postfix = "\n"
    receiving_directly_info = parse(output, prefix, postfix, 0)
    if receiving_directly_info == -1:
        print("    receiving_directly_info parsing Error")
        return False
    
    prefix = "taking "
    postfix = " seconds"
    receiving_directly_seconds = parse(receiving_directly_info, prefix, postfix, 0)
    if receiving_directly_seconds == -1:
        print("    receiving_directly_seconds parsing Error")
        return False

    prefix = " "
    postfix = " MB"
    receiving_directly_data = parse(receiving_directly_info, prefix, postfix, 0)
    if receiving_directly_data == -1:
        print("    receiving_directly_data parsing Error")
        return False
    
    prefix = "in "
    postfix = " rounds"
    receiving_directly_rounds = parse(receiving_directly_info, prefix, postfix, 0)
    if receiving_directly_rounds == -1:
        print("    receiving_directly_rounds parsing Error")
        return False
    
    prefix = "Receiving one-to-one"
    postfix = "\n"
    receiving_one_to_one_info = parse(output, prefix, postfix, 0)
    if receiving_one_to_one_info == -1:
        print("    receiving_one_to_one_info parsing Error")
        return False
    
    prefix = "taking "
    postfix = " seconds"
    receiving_one_to_one_seconds = parse(receiving_one_to_one_info, prefix, postfix, 0)
    if receiving_one_to_one_seconds == -1:
        print("    receiving_one_to_one_seconds parsing Error")
        return False

    prefix = " "
    postfix = " MB"
    receiving_one_to_one_data = parse(receiving_one_to_one_info, prefix, postfix, 0)
    if receiving_one_to_one_data == -1:
        print("    receiving_one_to_one_data parsing Error")
        return False
    
    prefix = "in "
    postfix = " rounds"
    receiving_one_to_one_rounds = parse(receiving_one_to_one_info, prefix, postfix, 0)
    if receiving_one_to_one_rounds == -1:
        print("    receiving_one_to_one_rounds parsing Error")
        return False
    
    prefix = "Sending directly"
    postfix = "\n"
    sending_directly_info = parse(output, prefix, postfix, 0)
    if sending_directly_info == -1:
        print("    sending_directly_info parsing Error")
        return False
    
    prefix = "taking "
    postfix = " seconds"
    sending_directly_seconds = parse(sending_directly_info, prefix, postfix, 0)
    if sending_directly_seconds == -1:
        print("    sending_directly_seconds parsing Error")
        return False

    prefix = " "
    postfix = " MB"
    sending_directly_data = parse(sending_directly_info, prefix, postfix, 0)
    if sending_directly_data == -1:
        print("    sending_directly_data parsing Error")
        return False
    
    prefix = "in "
    postfix = " rounds"
    sending_directly_rounds = parse(sending_directly_info, prefix, postfix, 0)
    if sending_directly_rounds == -1:
        print("    sending_directly_rounds parsing Error")
        return False
    
    prefix = "Sending one-to-one"
    postfix = "\n"
    sending_one_to_one_info = parse(output, prefix, postfix, 0)
    if sending_one_to_one_info == -1:
        print("    sending_one_to_one_info parsing Error")
        return False
    
    prefix = "taking "
    postfix = " seconds"
    sending_one_to_one_seconds = parse(sending_one_to_one_info, prefix, postfix, 0)
    if sending_one_to_one_seconds == -1:
        print("    sending_one_to_one_seconds parsing Error")
        return False

    prefix = " "
    postfix = " MB"
    sending_one_to_one_data = parse(sending_one_to_one_info, prefix, postfix, 0)
    if sending_one_to_one_data == -1:
        print("    sending_one_to_one_data parsing Error")
        return False
    
    prefix = "in "
    postfix = " rounds"
    sending_one_to_one_rounds = parse(sending_one_to_one_info, prefix, postfix, 0)
    if sending_one_to_one_rounds == -1:
        print("    sending_one_to_one_rounds parsing Error")
        return False
    
    return float(time), float(data), float(glob_data), int(rounds), int(integer_multiplications), int(integer_openings), float(online_seconds), float(data_online), int(online_rounds), float(offline_seconds), float(data_offline), int(offline_rounds), int(triples), float(cpu_time), float(broadcasting_seconds), float(broadcasting_data), int(broadcasting_rounds), float(exchanging_seconds), float(exchanging_data), int(exchanging_rounds), float(receiving_directly_seconds), float(receiving_directly_data), int(receiving_directly_rounds), float(receiving_one_to_one_seconds), float(receiving_one_to_one_data), int(receiving_one_to_one_rounds), float(sending_directly_seconds), float(sending_directly_data), int(sending_directly_rounds), float(sending_one_to_one_seconds), float(sending_one_to_one_data), int(sending_one_to_one_rounds)



def run_once(p, num_parties, squares_, triples_, inverses_, rounds_, args_0=None, args_1=None, args_2=None, verbose=False, pos=False):
    #TODO CAUTION
    if args_0 is not None:
        args = [RUN, "-p", "0", f"{p}-{args_0}-{args_1}-{args_2}", "-pn", PORT, "-ip", HOST_FILE, "-N", str(num_parties), "-v"]
        #print(args)
    else:
        args = [RUN, "-p", "0", f"{p}", "-pn", PORT, "-ip", HOST_FILE, "-N", str(num_parties), "-v"]
    if verbose:
        print("Running", args, flush=True)
    partyoutputs = []
    return0 = True

    try:
        partylist = []
        for i in range(num_parties):
            args[2] = str(i)
            partylist.append(Popen(args, stdin=PIPE, stdout=PIPE, stderr=STDOUT))

        for i in range(num_parties):
            partyoutputs.append(partylist[i].communicate(timeout=TIMEOUT)[0].decode("utf-8"))
            if (partylist[i].returncode != 0):
                return0 = False
    except Exception as ex:
        print("  Exception: " + str(ex), " at ", getcwd())
        return None

    if (return0 == False):
        print("  A party did not return 0", partylist)
        print(partylist[0], partyoutputs[0])
        return None
    if verbose:
        pass
    #print(partyoutputs[0])
    #print(squares_, triples_, inverses_, rounds_, print_triples(partyoutputs[0]))
    squares, triples, inverses, rounds = print_triples(partyoutputs[0])
    if not pos and (triples != triples_ or rounds != rounds_ or squares != squares_ or inverses != inverses_):
        print("    Expected squares/triples/inverses/rounds mismatch! Expected: " + str(squares) + " squares, " + str(triples) + " triples, " + str(inverses) + " inverses and " + str(rounds) + " rounds")
        print(squares_, triples_, inverses_, rounds_, print_triples(partyoutputs[0]))
        print("These expected numbers are extracted from ###BEGIN###\n", partyoutputs[0], "###END###")

    if partyoutputs[0].find("Correct", 0) == -1:
        print("    A Error occured during Computation!?", partyoutputs)

    """   
    times = [0] * num_parties
    datas = [0] * num_parties
    glob_datas = [0] * num_parties
    rounds_real = [0] * num_parties
    """
    all_datas = [ [0] * num_parties for i in range(32) ]

    for i in range(num_parties):
        if verbose:
            print("  Party " + str(i) + " output:")
        ret = stats(partyoutputs[i])
        if ret == False:
            print("    Error parsing output")
            continue
        #32
        time, data, glob_data, round, integer_multiplications, integer_openings, online_seconds, data_online, online_rounds, offline_seconds, data_offline, offline_rounds, triples, cpu_time, broadcasting_seconds, broadcasting_data, broadcasting_rounds, exchanging_seconds, exchanging_data, exchanging_rounds, receiving_directly_seconds, receiving_directly_data, receiving_directly_rounds, receiving_one_to_one_seconds, receiving_one_to_one_data, receiving_one_to_one_rounds, sending_directly_seconds, sending_directly_data, sending_directly_rounds, sending_one_to_one_seconds, sending_one_to_one_data, sending_one_to_one_rounds = ret
        if verbose:
            print("    Runtime: " + str(time) + " s")
            print("    Data sent: " + str(data) + " MB")
            print("    Global data sent: " + str(glob_data) + " MB")
            print(f"    Rounds: ~{round}")

        for j in range(32):
            all_datas[j][i] = ret[j]
        """times[i] = time
        datas[i] = data
        glob_datas[i] = glob_data
        rounds_real[i] = round"""

    if verbose:
        print()

    return all_datas#times, datas, glob_datas, rounds_real, rounds


def run(p, num_parties, squares_, triples_, inverses_, rounds_, runs, input_size, output_size, args_0=None, args_1=None, args_2=None, pos=False):
    print("Running '" + p + "' with " + str(num_parties) + " parties")
    vals = {}
    """av_time = [0] * num_parties
    av_data = [0] * num_parties
    av_glob_data = [0] * num_parties
    av_rounds = [0] * num_parties"""
    av_datas = [[0] * num_parties for i in range(32)]
    for run in range(runs):
        res = None
        while res == None:
            res = run_once(p, num_parties, squares_, triples_, inverses_, rounds_, args_0, args_1, args_2, VERBOSE, pos=pos)
            #print("res:",res)
        #times, datas, glob_datas, rounds, vm_rounds = res
        for i in range(num_parties):
            """av_time[i] += times[i]
            av_data[i] += datas[i]
            av_glob_data[i] += glob_datas[i]
            av_rounds[i] += rounds[i]"""
            for j in range(32):
                av_datas[j][i] += res[j][i]


    print("Average for " + str(runs) + " results per party:")
    for i in range(num_parties):
        print("  Party " + str(i) + ":")
        print("    Runtime: " + str(av_datas[0][i] / runs) + " s")
        vals[f"party {i} runtime"] = av_datas[0][i] / runs
        print("    Data sent: " + str(av_datas[1][i] / runs) + " MB")
        vals[f"party {i} data"] = av_datas[1][i] / runs
        print("    Global data sent: " + str(av_datas[2][i] / runs) + " MB")
        vals["global data"] = av_datas[2][i] / runs
        print("    Rounds: " + str(av_datas[3][i] / runs))
        vals[f"party {i} rounds"] = av_datas[3][i] / runs

        print("    Integer multiplications: " + str(av_datas[4][i] / runs) + " s")
        vals[f"party {i} integer multiplications"] = av_datas[4][i] / runs
        print("    Integer openings: " + str(av_datas[5][i] / runs) + " MB")
        vals[f"party {i} integer openings"] = av_datas[5][i] / runs
        print("    Triples: " + str(av_datas[12][i] / runs) + " MB")
        vals[f"party {i} triples"] = av_datas[12][i] / runs
        print("    CPU time: " + str(av_datas[13][i] / runs) + " s")
        vals[f"party {i} cpu time"] = av_datas[13][i] / runs

        print("    Online phase: " + str(av_datas[6][i] / runs) + " seconds " + str(av_datas[7][i] / runs) + " MB in " + str(av_datas[8][i] / runs) + " rounds")
        print("    Offline phase: " + str(av_datas[9][i] / runs) + " seconds " + str(av_datas[10][i] / runs) + " MB in " + str(av_datas[11][i] / runs) + " rounds")
    
        print("    Communication details:")
        print(f"   Broadcasting {av_datas[15][i] / runs} MB in {av_datas[16][i] / runs} rounds, taking {av_datas[14][i] / runs} seconds")
        print(f"   Exchanging one-to-one {av_datas[18][i] / runs} MB in {av_datas[19][i] / runs} rounds, taking {av_datas[17][i] / runs} seconds")
        print(f"   Receiving directly {av_datas[21][i] / runs} MB in {av_datas[22][i] / runs} rounds, taking {av_datas[20][i] / runs} seconds")
        print(f"   Receiving one-to-one {av_datas[24][i] / runs} MB in {av_datas[25][i] / runs} rounds, taking {av_datas[23][i] / runs} seconds")
        print(f"   Sending directly {av_datas[27][i] / runs} MB in {av_datas[28][i] / runs} rounds, taking {av_datas[26][i] / runs} seconds")
        print(f"   Sending one-to-one {av_datas[30][i] / runs} MB in {av_datas[31][i] / runs} rounds, taking {av_datas[29][i] / runs} seconds")

    print("VM rounds: ", rounds_)
    print()
    return vals


def compile(p, t, shared_ks, use_squares, verbose=True):
    if verbose:
        print("Compiling '" + p + "' for t = " + str(t), end="")
        print(", Shared Keyschedule = " + str(shared_ks) + ", Using Squares = " + str(use_squares))
    args = [COMPILE, PROGRAM_PATH + p + ".mpc", "-P", PRIME, str(t), str(use_squares), str(shared_ks)]
    if verbose:
        print(args)
    try:
        p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        #if verbose:
            #print("a",p.stdout.read(), args)
        output = p.communicate(timeout=TIMEOUT)[0].decode("utf-8")
        if verbose:
            print( "output is ", output)
    except Exception as ex:
        print("  Exception: " + str(ex))
        return False

    if p.returncode != 0:
        print("  Return code: " + str(p.returncode))
        return False

    postfix_square = " integer squares"
    postfix_triples = " integer triples"
    postfix_inverse = " integer inverses"
    postfix_depth = " virtual machine rounds"

    inverses = int(parse_line_before(output, postfix_inverse))
    triples = int(parse_line_before(output, postfix_triples))
    squares = int(parse_line_before(output, postfix_square))
    rounds = int(parse_line_before(output, postfix_depth))

    if inverses == -1:
        inverses = 0
    if squares == -1:
        squares = 0
    if triples == -1:
        triples = 0
    if rounds == -1:
        rounds = 0
    print("  Program requires " + str(squares) + " squares, " + str(triples) + " triples, " + str(inverses) + " inverses and " + str(rounds) + " rounds")
    print()
    return squares, triples, inverses, rounds

def write_hosts(num_parties):
    try:
        with open(HOST_FILE, "w") as f:
            for _ in range(num_parties):
                f.write(IP + "\n")
    except Exception as ex:
        print("Error writing to HOSTS file: " + str(ex))
        exit(-1)

@click.command()
@click.option('--runs', '-r', type=int, default=RUNS)
def main(runs):
    #write columns to result_file
    with open(result_file, "w") as f:
        for i,c in enumerate(cols):
            f.write(c)
            if i!=len(cols)-1:
                f.write(",")
            else:
                f.write("\n")  

    #run experiments
    for parties in [2,3,5,10,15,20]:#[2,3,5,10]:
        if parties == 2:
            ts = [4,8,16,32,64]
        else:
            ts = [4,8,16]
        for t in ts:
            if parties == 2:
                pt_lens_hash_pos = [4,8]
            else:
                pt_lens_hash_pos = [4]
            pt_lens_hash_hydra = [4]
            pt_lens_encrypt = [t]
            for p in PROGRAMS:
                if p in ["poseidon-2-0-hash", "poseidon-2-0-encrypt"]:
                    if p == "poseidon-2-0-encrypt":
                        pt_lens = pt_lens_encrypt
                        rates = [2]
                    else:
                        pt_lens = pt_lens_hash_pos
                        rates = [2,4]#,8]
                else:
                    rates = [None]
                    if p == "hydra-hash":
                        pt_lens = pt_lens_hash_hydra
                    elif p == "hydra-encrypt":
                        pt_lens = pt_lens_encrypt
                for r in rates:
                    for pt_len in pt_lens:
                        for use_squares in [0]:#[0, 1]:
                            print(f"!Running {p} with pt_len {pt_len} out_lne {t} rate {r} parties {parties}", flush=True)
                            vals = {}

                            if use_squares and p not in SQUARE_PROGRAMS:
                                continue
                            if p in ["poseidon-2-0-hash", "poseidon-2-0-encrypt"]:
                                ret = compile(p, r, t, pt_len)
                            else:
                                ret = compile(p, t, True, use_squares)
                            if ret == False:
                                continue
                            squares, triples, inverses, rounds = ret
                            vals["program"] = p
                            vals["using squares"] = use_squares
                            vals["integer triples"] = triples
                            vals["vm rounds"] = rounds
                            if r is not None:
                                vals["rate"] = r

                            
                            vals["input_len"] = pt_len
                            vals["output_len"] = t
                            vals["parties"] = parties
                            

                            write_hosts(parties)
                            print(time.now(), flush=True)
                            if p in ["poseidon-2-0-hash", "poseidon-2-0-encrypt"]:  
                                vs = run(p, parties, squares, triples, inverses, rounds, runs, pt_len, t,r, pt_len, t, pos=True)
                            else:
                                vs = run(p, parties, squares, triples, inverses, rounds, runs, 4, t)
    
                            vals.update(vs)

                            with open(result_file, "a") as f:
                                for i,c in enumerate(cols):
                                    v = vals.get(c)
                                    if v is not None:
                                        f.write(str(v))
                                    if i!=len(cols)-1:
                                        f.write(",")
                                    else:
                                        f.write("\n")
                            print(time.now(), flush=True)
                            

if __name__ == "__main__":
    main()
