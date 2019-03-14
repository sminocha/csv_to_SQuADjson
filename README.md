# csv_to_SQuADjson

# Overview

Script to convert a CSV containing Question, Context, and Answer triplets to a JSON in the format that can be ingested by a standard QA architecture. Output JSON format mirrors that of the SQuAD 2.0 dataset. 

# Download 

# Setup

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


# Run

# Acknowledgements

Raw train-v2.0.json (to determine correct JSON formatting) was pulled from [Chris Chute's squad repo](https://github.com/chrischute/squad/tree/master/data).

Adapted Chris Chute SQuAD pre-processing script. 

