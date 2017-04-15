# PCR Comment Automation

Using Amazon Mechanical Turk to review course comments.

## Getting Started
Start by running:

`pip install virtualenv`

`virtualenv venv`

`pip install -r requirements.txt`

`pip install --upgrade --user awscli`

	AWS Access Key ID: (specified in app.py)
	AWS Secret Access Key: (specified in app.py)
	Default region name: us-east-1
	Default output format: (skip!!!)

Finally, run

`python app.py`

## TODO

1. Clean up code
2. Prune requirements.txt
3. Config variables into separate file
4. Setup import of comments from database
5. Setup export of reviewed comments to database
6. Create full dictionary of words to filter
7. Add fuzzy matching to filter out word-lookalikes
8. Add comments/documentation
9. Determine payment per comment
10. Create a few more stupid dummy questions (during testing)
11. Replace stupid dummy questions with many smart dummy questions (after testing)
12. Clean up worker-view instructions
