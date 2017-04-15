ACCESS_ID = 'AKIAJTE3KKPD7JCT4UEQ'
SECRET_KEY = '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'
HOST = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

TITLE = 'Filter College Course Comments (WARNING: This HIT may contain adult content. Worker discretion is advised.)'
DESCRIPTION = ('Disapprove comments if they contain inappropriate content. Otherwise, approve them.')
REJECT_MESSAGE = "You failed to provide a correct response to one or more questions. Sorry for the inconvenience. We hope to work with you again in the future."
KEYWORDS = 'censor, comments, filter'
SECONDS_TO_EXPIRE = 60*5

XML_TEMPLATE = "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd"

# TODO: need to add more and filter out all building names
WORDS_TO_FILTER = ["pennsylvania", "penn", "philadelphia", "philly", "M&T", "LSM", "MLS", "Franklin", "Moore", "Towne", "Hunstsman", "Levine"]

DUMMY_QUESTIONS = [{"question": "dummy-approve", "answer": "approve"}, {"question": "dummy-reject", "answer": "disapprove"}, {"question": "dummy-approve", "answer": "approve" }]

courses = [{'course': 'CIS 110', 'instructors': ['Benedict Brown', 'Arvind Bhusnurmath'], 'comments': ['I hated this class so much. Brown and Arvind were the worst professors everat the UNIVERsity of PENNSYLVANIA. I dont like that we took field trips around philly either. As an M&T student this was a waste of my time. The end', 'I really wish the instruction was better. I do not like walking out to moore, just to be held captive by recitation for an hour. I wish I had dropped CIS110.']},
                {'course': 'CIS 120', 'instructors': ['Benedict Brown', 'Arvind Bhusnurmath'], 'comments': ['I hated this class so much. Brown and Arvind were the worst professors everat the UNIVERsity of PENNSYLVANIA. I dont like that we took field trips around philly either. As an M&T student this was a waste of my time. The end', 'I really wish the instruction was better. I do not like walking out to moore, just to be held captive by recitation for an hour. I wish I had dropped CIS110.']}]

swearwords = [ "arse", "ass", "asshole", "bastard", "bitch", "bollocks", "child-fucker", "crap", "cunt",
                "damn", "damm", "fuck", "fucker", "fucking", "godamm", "goddam", "goddamm", "godamn", "goddamn",
                "hell", "motherfucker", "nigga", "nigger", "shit", "shitass", "twat"]
