'''
Script to convert a CSV containing Question, Context, and Answer triplets to a JSON in the format that can be ingested by a standard QA architecture. Output JSON format mirrors that of the SQuAD 2.0 dataset. 

Raw train-v2.0.json (to determine correct JSON formatting) pulled from Chris Chute's squad repo (https://github.com/chrischute/squad/tree/master/data).

Adapted Chris Chute SQuAD pre-processing script. 
'''


'''
TODO: probably separate scripts to output train-v2.0.json, dev-v2.0.json, and test-v2.0.json
TODO: look into differences between potential hard coded train vs. dev vs. test solution
TODO: currently going to treat input as lists of length 3, corresponding to Q, C, A 

Assumes input csv columns are in the format C, Q, A

SQuAD JSON Structure: 

{"data": [{
    "title": , 
    "paragraphs": [{
        "qas": [
            {"question": , "id": , "answers": [{"text": , "answer_start": }], "is_impossible": },
            {"question": , "id": , "answers": [{"text": , "answer_start": }], "is_impossible": },
            {"question": , "id": , "answers": [{"text": , "answer_start": }], "is_impossible": }
        ]
        "context":
    }, {
        "qas": [...]
        "context": 
    }]
}] }
'''

"""Script to make custom SQuAD dataset."""

import argparse
import csv
import random
import string
import ujson as json


def main(args):
    # Seed for reproducible IDs
    random.seed(0)

    # Read new hand-labelled paragraphs
    new_paragraphs = get_paragraphs(args.csv_path)

    # Dump new paragraphs to a json file
    new_data = {'title': 'NewData',
                'paragraphs': [p.to_dict() for p in new_paragraphs]}

    # Read training set
    with open(args.orig_train_path, 'r') as json_fh:
        orig_train_data = json.load(json_fh)
        

    # Add new paragraphs to training set
    train_data = orig_train_data['data']
    # print("LENGTH ORIGINAL: ". len(train_data))
    train_data.append(new_data)
    print('Num train: {}'.format(sum(1 for data in train_data
                                   for paragraph in data['paragraphs']
                                   for _ in paragraph['qas'])))

    # Save custom train set
    print('Saving new training set to {}...'.format(args.new_train_path))
    with open(args.new_train_path, 'w') as json_fh:
        train_dict = {'version': 'v2.0', 'data': train_data}
        json.dump(train_dict, json_fh)


def get_paragraphs(custom_path):
    paragraphs = []

    curr_context = None
    curr_qas = []
    with open(custom_path, newline='') as csv_fh:
        csv_reader = csv.reader(csv_fh, delimiter=',')
        row_break_count = 0
        for row in csv_reader:
            print("CUSTOM PATH, Question: ", row[0])
            print("CUSTOM PATH, Context: ", row[1])
            print("CUSTOM PATH, Answer: ", row[2])
            # Read all columns into a QA pair
            question = None
            answers = []
            is_impossible = False
            print("ENUMERATION: ")
            print(col_text for col_idx, col_text in enumerate(row))
            for col_idx, col_text in enumerate(row[:5]):
                print("col_idx: ", col_idx)
                print("col_text: ", col_text)
                if col_idx == 0 and col_text:
                    # Reset when we see a new context
                    if curr_context is not None:
                        paragraphs.append(Paragraph(curr_context, curr_qas))
                    curr_context = col_text
                    curr_qas = []
                # Add new qa pair
                if col_idx == 1:
                    question = col_text
                elif col_idx >= 2:
                    if col_idx == 2 and col_text.upper() == 'NO_ANSWER':
                        is_impossible = True
                    if not is_impossible:
                        answer = {'text': col_text,
                                  'answer_start': curr_context.find(col_text)}
                        answers.append(answer)

            # Add QA to the current list
            curr_QA = QA(question, new_uuid(), answers, is_impossible)
            curr_qas.append(curr_QA)
            print("CURR QA Question: ", curr_QA.question)
            print("CURR QA ANSWERS: ", curr_QA.answers)
            print("CURR QA ID: ", curr_QA.uuid)
            print("CURR QA is_impossible: ", curr_QA.is_impossible)

            row_break_count += 1

            if row_break_count >= 2:
                print("BREAKING")
                break
    print("CURR QAs: ", curr_qas[0])
    print("SHOULD BE EMPT...")
    print("PARAGRSAPHS: ", paragraphs)
    return paragraphs


def new_uuid(length=25):
    """Get a new UUID string of lowercase hexadecimal digits."""
    letters = [random.choice(string.hexdigits) for _ in range(length)]
    return ''.join(letters).lower()


class QA:
    """Holds a question-answer pair.

    Args:
        question (str): Question text.
        uuid (str): UUID of length 25, hexadecimal digits only.
        answers (list): List of dicts with 'text', 'answer_start' keys.
        is_impossible (bool): Question has no answer.
    """
    def __init__(self, question, uuid, answers, is_impossible):
        self.question = question
        self.uuid = uuid
        self.answers = answers
        self.is_impossible = is_impossible

    def to_dict(self):
        return {
            'question': self.question,
            'id': self.uuid,
            'answers': self.answers,
            'is_impossible': self.is_impossible,
        }


class Paragraph:
    """Holds a paragraph with a context and one or more question-answer pairs.

    Args:
        context (str): Context.
        qas (list): List of `QA` objects.
    """
    def __init__(self, context, qas):
        self.context = context
        self.qas = qas

    def to_dict(self):
        return {
            'context': self.context,
            'qas': [qa.to_dict() for qa in self.qas]
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Make custom SQuAD for CS224n')

    parser.add_argument('--csv_path', type=str, default='data/custom_squad.csv')
    parser.add_argument('--new_train_path', type=str, default='data/new-train-v2.0.json')
    parser.add_argument('--orig_train_path', type=str, default='data/train-v2.0.json')

    main(parser.parse_args())

    # LINE TO RUN FOR DEBUG: python to_SQuADjson.py --csv_path=output.csv --new_train_path=new-train-v2.0.json --orig_train_path=train-v2.0.json