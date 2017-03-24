import re
import boto3
import datetime
import math
import random

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

courses = [{'course': 'CIS 110', 'instructors': ['Benedict Brown', 'Arvind Bhusnurmath'], 'comments': ['I hated this class so much. Brown and Arvind were the worst professors everat the UNIVERsity of PENNSYLVANIA. I dont like that we took field trips around philly either. As an M&T student this was a waste of my time. The end', 'I really wish the instruction was better. I do not like walking out to moore, just to be held captive by recitation for an hour. I wish I had dropped CIS110.']}, {'course': 'CIS 120', 'instructors': ['Benedict Brown', 'Arvind Bhusnurmath'], 'comments': ['I hated this class so much. Brown and Arvind were the worst professors everat the UNIVERsity of PENNSYLVANIA. I dont like that we took field trips around philly either. As an M&T student this was a waste of my time. The end', 'I really wish the instruction was better. I do not like walking out to moore, just to be held captive by recitation for an hour. I wish I had dropped CIS110.']}]


overview = "<Overview>"
overview = overview + '<Title>Censor vulgar, overly harsh, irrelevant, or unconstructive college course comments.</Title>'
overview = overview + '<Text>Here we are some examples of what we are looking for: 1. This professor was a jerk. F*** this class. -> Disapprove (Vulgar) 2. This was the worst class. -> Disapprove (Unconstructive)  3. This was an amazing class. -> Approve  4. I truly did not enjoy this class. The professor was too fast and the homework was unrelated to exams. XXXXXX is too hard and way too boring. I strongly advise against this class. -> Approve (strongly negative, but reserved)</Text>'

overview = overview + "</Overview>"

def add_comment(text, id, question_form):
    qc1 = "<Question><QuestionIdentifier>" + id + "</QuestionIdentifier>"
    qc1 = qc1 + "<DisplayName>" + "Question1" + "</DisplayName>" 
    qc1 = qc1 + "<IsRequired>true</IsRequired>"
    qc1 = qc1 + "<QuestionContent><Text>" + text  + "</Text></QuestionContent>"
    qc1 = qc1 + "<AnswerSpecification>"
    qc1 = qc1 + "<SelectionAnswer><StyleSuggestion>radiobutton</StyleSuggestion>"
    qc1 = qc1 + "<Selections>"
    qc1 = qc1 + "<Selection><SelectionIdentifier>approve</SelectionIdentifier><Text>Approve</Text></Selection>"
    qc1 = qc1 + "<Selection><SelectionIdentifier>disapprove</SelectionIdentifier><Text>Disapprove</Text></Selection>"
    qc1 = qc1 + "</Selections></SelectionAnswer></AnswerSpecification></Question>"
    question_form = question_form + qc1
    return question_form

def filter_comment(comment, professors, course):
    to_filter = WORDS_TO_FILTER
    for c in course.split(" "):
        to_filter.append(c)
    for w in to_filter:
        ignore_case = re.compile(re.escape(w), re.IGNORECASE)
        comment = ignore_case.sub("".join(['X' for c in w]), comment)
    for i in range(0, len(professors)):
        professors[i] = professors[i].replace(',', '')
        for name in professors[i].split(' '):
            ignore_case = re.compile(re.escape(name), re.IGNORECASE)
            comment = ignore_case.sub("".join(['X' for c in name]), comment)
    return comment

for c in courses:
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
 
    question_form = "<QuestionForm xmlns='" + XML_TEMPLATE  + "'>" + overview
    dummies_issued = 0
    for i in range(0, len(c["comments"]) + num_of_dummy_questions):
        if i+1 in dummy_question_ids:
            dummy_question = DUMMY_QUESTIONS[id_to_question[str(i+1)]]["question"]
            question_form = add_comment(dummy_question, "Question"+str(i+1), question_form)
            dummies_issued = dummies_issued + 1
        else:
            question_form = add_comment(filter_comment(c["comments"][i - dummies_issued], c['instructors'], c['course']), "Question"+str(i+1), question_form)
    
    question_form = question_form + "</QuestionForm>"
    mtc.create_hit(Question=question_form,
                   MaxAssignments=1,
                   Title=TITLE,
                   Description=DESCRIPTION,
                   Keywords=KEYWORDS,
                   AssignmentDurationInSeconds=90*(len(c["comments"])),
                   LifetimeInSeconds=SECONDS_TO_EXPIRE,
                   AssignmentReviewPolicy=reviewPolicy,
                   Reward="1")
