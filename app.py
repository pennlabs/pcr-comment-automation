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
        tokenizedComments.append(word_tokenize(c));

    return tokenizedComments

# MAIN FILTER FUNCTION
def filter_comment(course):
    for c in course:
        filtered_c = remove_vulgar_comments(c['comments'])

# Fitler Step 1
def remove_vulgar_comments(comment):

    tokenizedComments = tokenize(comment)
    toRemove = []
    count = 0

    # for c in tokenizedComments:
    #     for word in swearwords:
    #         if word in c:
    #             print c
    #             print 'no'
    #             print word
    #             print count
    #             toRemove[count] = True
    #     count = count + 1

# Swaps pairs of characters given a list of strings; designed to create a list of common potential typos
def swap_chars(string_list):
    corrections = set()
    for str in string_list:
        for i in range(len(str) - 1):
            rest = None
            if i < len(str) - 1:
                rest = str[(i+2):]
            else: rest = ""
            potentialWord = str[0:i] + str[i + 1] + str[i] + rest
            corrections.add(potentialWord)
    return list(corrections)

def permute_chars(string_list):
    corrections = set()
    for str in string_list:
        for i in range(len(str) - 1):
            for x in range(97, 123):
                new_str = str[0:i] + chr(x) + str[(i+1):]
                corrections.add(new_str)
            sub_str = str[0:i] + str[(i+1):]
            corrections.add(sub_str)
    return list(corrections)

def generateHitRequest():

    css = [{'course': 'CIS 110', 'instructors': ['Benedict Brown', 'Arvind Bhusnurmath'], 'comments': ['I fuck this" class so > much. fuck and Arvind asshole were the worst professors everat the UNIVERsity of PENNSYLVANIA. I dont like that we took field trips around philly either. As an M&T student this was a waste of my time. The end', 'I really wish the instruction was better. I do not like walking out to moore, just to be held captive by recitation for an hour. I wish I had dropped CIS110.']},
                    {'course': 'CIS 120', 'instructors': ['Benedict Brown', 'Arvind Bhusnurmath'], 'comments': ['I hated this class so much. Brown  bitch and Arvind were the worst professors everat the UNIVERsity of PENNSYLVANIA. I dont like that we took field trips around philly either. As an M&T student this was a waste of my time. The end', 'I really wish the instruction was better. I do not like walking out to moore, just to be held captive by recitation for an hour. I wish I had dropped CIS110.']}]

    filter_comment(css)

    # with open('strings.json') as json_data:
    #     d = json.load(json_data)
    #     print(d)

    for c in courses:
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


#     comment = remove_vulgar_comments(prefiltered)
#     to_filter = WORDS_TO_FILTER
#
#     for c in course.split():
#         to_filter.append(c)
#     for w in to_filter:
#         ignore_case = re.compile(re.escape(w), re.IGNORECASE)
#         comment = ignore_case.sub("".join(['X' for c in w]), comment)
#     for i in range(0, len(professors)):
#         professors[i] = professors[i].replace(',', '')
#         for name in professors[i].split(' '):
#             ignore_case = re.compile(re.escape(name), re.IGNORECASE)
#             comment = ignore_case.sub("".join(['X' for c in name]), comment)
#     return comment
