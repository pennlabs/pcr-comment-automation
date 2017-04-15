import re
import boto3
import datetime
import math
import random
import json
from data import *
from nltk.tokenize import word_tokenize
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring
import numpy as np
from itertools import compress  
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

mtc = boto3.client("mturk", aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      endpoint_url=HOST)

def add_comment(text, qid):

    tree = ET.parse('comment.xml')

    qID = tree.find('QuestionIdentifier')
    dispName = tree.find('DisplayName')
    txt = tree.find('QuestionContent')

    qID.text = qid
    dispName.text = qid
    txt[0].text = text

    root = tree.getroot()
    return root

# Helper function used frequently
def tokenize(comment):

    tokenizedComments = []
    count = 0

    for c in comment:
        c = c.lower();
        tokenizedComments.append(word_tokenize(c));

    return tokenizedComments


# MAIN FILTER FUNCTION
def filter_comment(course):

    for c in course:
        c['comments'] = remove_vulgar_comments(c['comments'])

    filtered_data = fuzzFilter(course)
    return filtered_data

# Fitler Step 1
def remove_vulgar_comments(comment):

    tokenizedComments = tokenize(comment)
    toKeep = np.full( len(comment), True)
    count = 0

    for c in tokenizedComments:
        for word in swearwords:
            if word in c:
                toKeep[count]= False
        count = count + 1;

    comment = list(compress(comment, toKeep))
    return comment

# Filter Step 2
def fuzzFilter(data):
    
    course_num = 0

    # For each course
    while course_num < len(data):
        comment_num = 0
        comment_list = data[course_num]["comments"]
        # For each comment in each course
        while comment_num < len(comment_list):
            tok_index = 0
            tokens = tokenize(comment_list)
            currTokSet = tokens[comment_num]
            # Iterate over each tokenized word in comment
            for word in currTokSet:
                for keyword in WORDS_TO_FILTER:
                    #filter based on Levenshtein Distance 
                    if fuzz.ratio(word, keyword) >= 90:
                        currTokSet[tok_index] = "*****"
                tok_index = tok_index + 1
            newComment = ' '.join(currTokSet)
            data[course_num]["comments"][comment_num] = newComment
            comment_num = comment_num + 1
        course_num = course_num + 1
        return data

def generateHitRequest():

    filtered = filter_comment(courses)

    for c in filtered:
        qtree = ET.parse('questionform.xml')
        qroot = qtree.getroot()
        qroot.set('xmlns', XML_TEMPLATE)

        ovTree = ET.parse('overview.xml')
        ovRoot = ovTree.getroot()
        qroot.append(ovRoot);

        num_of_dummy_questions = int(math.ceil(0.1*len(c["comments"])))
        dummy_question_ids = random.sample(range(1, len(c["comments"]) + num_of_dummy_questions + 1), num_of_dummy_questions)
        dummy_question_ref = random.sample(range(1, len(DUMMY_QUESTIONS)), num_of_dummy_questions)
        id_to_question = {}
        for d in range(0, len(dummy_question_ids)):
            id_to_question[str(dummy_question_ids[d])] = dummy_question_ref[d]

        reviewPolicy = {
            "PolicyName": "ScoreMyKnownAnswers/2011-09-01",
            "Parameters": [
                {"Key": "ApproveIfKnownAnswerScoreIsAtLeast", "Values": [str(num_of_dummy_questions)]},
                {"Key": "RejectIfKnownAnswerScoreIsLessThan", "Values": [str(num_of_dummy_questions)]},
                {"Key": "ExtendIfKnownAnswerScoreIsLessThan", "Values": [str(num_of_dummy_questions)]},
                {"Key": "RejectReason", "Values": [REJECT_MESSAGE]},
                {"Key": "AnswerKey", "MapEntries": [{"Key": "Question" + str(i), "Values": [DUMMY_QUESTIONS[id_to_question[str(i)]]["answer"]]} for i in dummy_question_ids]}
            ]
        }

        dummies_issued = 0
        for i in range(0, len(c["comments"]) + num_of_dummy_questions):
            if i+1 in dummy_question_ids:
                dummy_question = DUMMY_QUESTIONS[id_to_question[str(i+1)]]["question"]
                qfroot = add_comment(dummy_question, "Question"+str(i+1))
                qroot.append(qfroot)
                dummies_issued = dummies_issued + 1
            else:
                qfroot = add_comment(c["comments"][i - dummies_issued], "Question"+str(i+1))
                qroot.append(qfroot)

        question_form = ET.tostring(qroot, encoding='utf-8', method='xml')

        mtc.create_hit(Question=question_form,
                       MaxAssignments=1,
                       Title=TITLE,
                       Description=DESCRIPTION,
                       Keywords=KEYWORDS,
                       AssignmentDurationInSeconds=90*(len(c["comments"])),
                       LifetimeInSeconds=SECONDS_TO_EXPIRE,
                       AssignmentReviewPolicy=reviewPolicy,
                       Reward="1")

if __name__ == '__main__':
    generateHitRequest()

