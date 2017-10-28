import random
import json
from data import *
from tokenizer import *
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring
import numpy as np
from itertools import compress
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

ACCESS_ID = 'AKIAJTE3KKPD7JCT4UEQ'
SECRET_KEY = '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'
HOST = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

mtc = boto3.client("mturk", aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      endpoint_url=HOST)

TITLE = 'Filter College Course Comments (WARNING: This HIT may contain adult content. Worker discretion is advised.)'
DESCRIPTION = ('Disapprove comments if they contain inappropriate content. Otherwise, approve them.')
KEYWORDS = 'censor, comments, filter'
SECONDS_TO_EXPIRE = 60*5

XML_TEMPLATE = "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd"

# TODO: Refactor into data files
WORDS_TO_FILTER = ["pennsylvania", "penn", "philadelphia", "philly", "M&T", "LSM", "MLS", "Franklin", "Moore", "Towne", "Hunstsman", "Levine"] #need to add more and filter out all building names

DUMMY_QUESTIONS = [{"question": "dummy-approve", "answer": "approve"}, {"question": "dummy-reject", "answer": "disapprove"}, {"question": "dummy-approve", "answer": "approve" }]

REJECT_MESSAGE = "You failed to provide a correct response to one or more questions. Sorry for the inconvenience. We hope to work with you again in the future."

courses = [{'course': 'CIS 110', 'instructors': ['Benedict Brown', 'Arvind Bhusnurmath'], 'comments': ['I hated this class so much. Brown and Arvind were the worst professors everat the UNIVERsity of PENNSYLVANIA. I dont like that we took field trips around philly either. As an M&T student this was a waste of my time. The end', 'I really wish the instruction was better. I do not like walking out to moore, just to be held captive by recitation for an hour. I wish I had dropped CIS110.']},
            {'course': 'CIS 120', 'instructors': ['Benedict Brown', 'Arvind Bhusnurmath'], 'comments': ['I hated this class so much. Brown and Arvind were the worst professors everat the UNIVERsity of PENNSYLVANIA. I dont like that we took field trips around philly either. As an M&T student this was a waste of my time. The end', 'I really wish the instruction was better. I do not like walking out to moore, just to be held captive by recitation for an hour. I wish I had dropped CIS110.']}]


def add_comment(text, qid):

    tree = ET.parse('comment.xml')

    qID = tree.find('QuestionIdentifier')
    qID.text = qid

    dispName = tree.find('DisplayName')
    dispName.text = qid

    txt = tree.find('QuestionContent')
    txt[0].text = text

    root = tree.getroot()
    return root

# Top-level filter function: filters out vulgar comments and censors keywords.
def filter_comment(comment, professors, course):
    # Filter Step 1
    for c in course:
        c['comments'] = remove_vulgar_comments(c['comments'])
    # Filter Step 2
    filtered_data = fuzzFilter(course)
    return filtered_data

def remove_vulgar_comments(comment):
    tokenizedComments = tokenizeSwearWords(comment)
    toKeep = np.full(len(comment), True)
    count = 0
    # Keep a list of "flags" that indicate whether a comment contains a vulgar word.
    for c in tokenizedComments:
        for word in swearwords:
            if word in c:
                toKeep[count] = False
                count = count + 1
    # Remove comments from the original data depending on whether the comment was flagged.
    comment = list(compress(comment, toKeep))
    return comment

def tokenizeSwearWords(comment):
    tokenizedComments = []
    count = 0
    for c in comment:
        c = c.lower();
        tokenizedComments.append(tokenize(c));
    return tokenizedComments

# Filter Step 2: censors words based on keywords found using a maximum Levinshtein distance.
 def fuzzFilter(data):
     course_num = 0

     # For each course...
     while course_num < len(data):
         comment_num = 0
         comment_list = data[course_num]["comments"]
         # For each comment in each course...
         while comment_num < len(comment_list):
             tok_index = 0
             # Tokenize the current comment using the tokenizer.
             curr_tok_set = tokenize(comment_list[comment_num])

             # Iterate over each tokenized word in comment.
             for word in currTokSet:
                 for keyword in WORDS_TO_FILTER:
                     # Make words case-insensitive for comparison purposes
                     lcword = word.lower()
                     lckeyword = keyword.lower()

                     # Filter based on Levenshtein Distance. The fuzz library
                     # returns a "fuzz ratio" that is between 0 and 100, with 100
                     # being an identical match to the word being compared.
                     if fuzz.ratio(lcword, lckeyword) >= 90:
                         curr_tok_set[tok_index] = "*****"
                 tok_index = tok_index + 1

             # Reparse the tokens into one string.
             newComment = ''.join(curr_tok_set)

             # Replace the old comment in the raw data with the censored comment.
             data[course_num]["comments"][comment_num] = newComment

             comment_num = comment_num + 1
         course_num = course_num + 1
     return data

 # Adds instructors and course names to the list of words to filter.
 def addNamesToWordsToFilter(data):
     for course in data:
         for prof in course["instructors"]:
             # Tokenize first and last names of instructors. Important since most
             # comments don't use the instructor's full name.
             for name in prof.split():
                 WORDS_TO_FILTER.append(name)
         WORDS_TO_FILTER.append(course["course"])

# Connects with MT and uploads a HIT request.
def generateHitRequest():
    # Build filter list and filter comments.
    addNamesToWordsToFilter(courses)
    filtered = filter_comment(courses)

    for c in filtered:
        qtree = ET.parse('questionform.xml')
        qroot = qtree.getroot()
        qroot.set('xmlns', XML_TEMPLATE)

        ovTree = ET.parse('overview.xml')
        ovRoot = ovTree.getroot()
        qroot.append(ovRoot);

        num_of_dummy_questions = int(math.ceil(0.1 * len(c["comments"])))
        dummy_question_ids = random.sample(range(1, len(c["comments"]) + num_of_dummy_questions + 1),
                                           num_of_dummy_questions)
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
                {"Key": "AnswerKey", "MapEntries": [
                    {"Key": "Question" + str(i), "Values": [DUMMY_QUESTIONS[id_to_question[str(i)]]["answer"]]} for i in
                    dummy_question_ids]}
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

        question_form = ET.tostring(qroot, encoding='utf-8', method='xml').decode("utf-8")

        ptree = ET.parse('reward.xml')
        proot = ptree.getroot()
        reward_form = ET.tostring(proot, encoding='utf-8', method='xml')

        mtc.create_hit(Question=question_form.decode(),
                       MaxAssignments=1,
                       Title=TITLE,
                       Description=DESCRIPTION,
                       Keywords=KEYWORDS,
                       AssignmentDurationInSeconds=30*(len(c["comments"])),
                       LifetimeInSeconds=SECONDS_TO_EXPIRE,
                       AssignmentReviewPolicy=reviewPolicy,
                       Reward="0.2",
                       )

      # Uncomment the following lines to test filter results on the command linewithout making a HIT request.
      # addNamesToWordsToFilter(courses)
      # filtered = filter_comment(courses)
      # print(filtered)

# Calls on the HIT request.
if __name__ == '__main__':
    generateHitRequest()
