import re
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import QuestionContent, Question, QuestionForm, Overview, AnswerSpecification, SelectionAnswer, FormattedContent

ACCESS_ID = 'AKIAJTE3KKPD7JCT4UEQ'
SECRET_KEY = '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'
HOST = 'mechanicalturk.sandbox.amazonaws.com'

mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)

title = 'Filter Course Comments'
description = ('Censor comments if they contain inappropriate content. ')
keywords = 'censor, comments, filter'

ratings = [
    ('Approve', '1'),
    ('Disapprove', '0')
]

# TODO: Refactor into data files
words_to_filter = ["pennsylvania", "penn", "philadelphia", "philly", "M&T", "LSM", "MLS", "Franklin", "Moore", "Towne", "Hunstsman", "Levine"] #need to add more and filter out all building names

courses = [{'course': 'CIS 110', 'instructors': ['Benedict Brown', 'Arvind Bhusnurmath'], 'comments': ['I hated this class so much. Brown and Arvind were the worst professors everat the UNIVERsity of PENNSYLVANIA. I dont like that we took field trips around philly either. As an M&T student this was a waste of my time. The end', 'I really wish the instruction was better. I do not like walking out to moore, just to be held captive by recitation for an hour. I wish I had dropped CIS110.']}, {'course': 'CIS 120', 'instructors': ['Benedict Brown', 'Arvind Bhusnurmath'], 'comments': ['I hated this class so much. Brown and Arvind were the worst professors everat the UNIVERsity of PENNSYLVANIA. I dont like that we took field trips around philly either. As an M&T student this was a waste of my time. The end', 'I really wish the instruction was better. I do not like walking out to moore, just to be held captive by recitation for an hour. I wish I had dropped CIS110.']}]

overview = Overview()
overview.append_field('Title', 'Censor vulgar, overly harsh, irrelevant, or unconstructive college course comments.')
overview.append(FormattedContent('<strong>Here we are some examples of what we are looking for: <br/> 1. This professor was a jerk. F*** this class. -> Disapprove (Vulgar)<br/> 2. This was the worst class. -> Disapprove (Unconstructive) <br/> 3. This was an amazing class. -> Approve <br/> 4. I truly did not enjoy this class. The professor was too fast and the homework was unrelated to exams. XXXXXX is too hard and way too boring. I strongly advise against this class. -> Approve (strongly negative, but reserved) <br/> </strong>'))


question_form = QuestionForm()
question_form.append(overview)


def addComment(text):
    qc1 = QuestionContent()
    qc1.append(FormattedContent(text))
    fta1 = SelectionAnswer(min=1, max=1, style='dropdown', selections=ratings,
                           type='text', other=False)
    q1 = Question(identifier='design', content=qc1,
                  answer_spec=AnswerSpecification(fta1), is_required=True)
    question_form.append(q1)


def filter_comment(comment, professors, course):
    to_filter = words_to_filter
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


def get_all_reviewable_hits(mtc):
    page_size = 50
    hits = mtc.get_reviewable_hits(page_size=page_size)
    print "Total results to fetch %s " % hits.TotalNumResults
    print "Request hits page %i" % 1
    total_pages = float(hits.TotalNumResults)/page_size
    int_total = int(total_pages)
    if total_pages - int_total > 0:
        total_pages = int_total + 1
    else:
        total_pages = int_total
    pn = 1
    while pn < total_pages:
        pn += 1
        print "Request hits page %i" % pn
        temp_hits = mtc.get_reviewable_hits(page_size=page_size,
                                            page_number=pn)
        hits.extend(temp_hits)
    for hit in hits:
        assignments = mtc.get_assignments(hit.HITId)
        for assignment in assignments:
            print "Answers of the worker %s" % assignment.WorkerId
            for question_form_answer in assignment.answers:
                for resp in question_form_answer:
                    print resp.fields
            mtc.approve_assignment(assignment.AssignmentId)
            print "--------------------"

# get_all_reviewable_hits(mtc)
for c in courses:
    question_form = QuestionForm()
    question_form.append(overview)
    for com in c['comments']:
        addComment(filter_comment(com, c['instructors'], c['course']))
    mtc.create_hit(questions=question_form,
                   max_assignments=5,
                   title=title,
                   description=description,
                   keywords=keywords,
                   duration=60*5,
                   # HITReviewPolicy = "Comments",
                   reward=1)
