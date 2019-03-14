'''
test preprocessing script, benefit cosmetics dataset. 
'''

import csv
import json
import sys
from collections import deque
# from itertools import map

# constants
reply_substrings = ['Hi gorgeous!', 'Hi, gorgeous!', ' xo']
no_answer_substrings = ['email us', 'Email']

def main():
    filename = 'US_DM_conversations.csv'
    output_filename = 'output.json'
    raw_csv = ingest_csv(filename)
    QCA_triplets = construct_triplets(raw_csv)

    # CHECKING OUTPUTS, FIRST PASS PREPROCESSING SCRIPT
    print(QCA_triplets[0])
    ex_Q, ex_C, ex_A = QCA_triplets[1]

    print("Question: ", ex_Q)
    print("Context: ", ex_C)
    print("Answer: ", ex_A)
    print("LENGTH: ", len(QCA_triplets)) # 3.3k, down from 20k after first pass...
    write_json(output_filename, QCA_triplets)


# if run into OOM issues, revisit this (don't want to create entire list in memory)
# potential alternative could be outputting or writing each QCA triplet one at a time
def ingest_csv(filename):
    with open(filename, 'r') as raw:
        reader = csv.reader(raw)
        
        raw_csv = deque(reader)
        # include writing to CSV functionality here

    raw.close()

    return raw_csv

'''
Write output to JSON. Will eventually concatenate onto train-v2.0.json, without randomly sampling, the batching will simulate that random sampling.


FIGURE OUT WHICH DIALECT TO USE
WRITE TO MULTIPLE ROWS 
'''
# def write_csv(output_filename, to_csv):
#     # 
#     with open("output.csv",'w') as results_file:
#         writer = csv.writer(results_file, dialect='excel')
#         writer.writerows(to_csv)

#     results_file.close()

def write_json(output_filename, to_json): 
    # declare field names, which json writer will use to dump file to JSON format. 
    fieldnames = ("Question","Context","Answer")
    
    json_writer = open(output_filename, 'w')

    # for row in to_json:
    #     json.dump(row, json_writer)
    #     json_writer.write('\n')
    json_output = json.dumps(to_json)
    json_writer.write(json_output)

    json_writer.close()

'''
Encoding the following logic to construct each Q, C, A datapoint:

-Check if message contains a '?'
-Throw away if message contains 'hey gorgeous' or any related phrases
-If message contains a '?', following message should be treated as context. 
-Splice out from context 'hey gorgeous' or any related phrases
-Turn candidate context into empty string if it contains any no_answer_substrings
-Extract 'ground truth' answer from context by treating up to first punctuation as answer
'''    
def construct_triplets(raw_csv):
    QCA_triplets = []
    # while raw_csv still has data in it...
    while len(raw_csv) > 0:
        # initialize current row with pop
        thread_id, thread_sender, message, timestamp, sender = raw_csv.pop()
        
        # check if message contains any of the reply_substrings
        # if message is a valid quesiton, follow through with triplet logic
        if any(list(map(message.__contains__, reply_substrings))) == False:
            candidate_Q = message

            # check if message contains a '?'
            if '?' in candidate_Q:
                candidate_C = raw_csv.pop()[2]


                # splice out any of reply_substrings from candidate_C
                for reply_substring in reply_substrings:
                    if reply_substring in candidate_C:
                        candidate_C.replace(reply_substring, '')

                candidate_A = 'No_Answer'
                # turn candidate context into empty string if it contains any no_answer_substrings
                if any(list(map(candidate_C.__contains__, reply_substrings))):
                    candidate_C = ''
                    
                # treat up to first punctuation as answer (extracted from context)
                if candidate_C != '':
                    if '!' in candidate_C:
                        candidate_A = candidate_C.split('!')[0]
                    if '.' in candidate_C:
                        candidate_A = candidate_C.split('.')[0]

                QCA_triplets.append([candidate_Q, candidate_C, candidate_A])

    return QCA_triplets

if __name__ == '__main__':
    main()


