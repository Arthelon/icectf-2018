from requests_html import HTML
import requests
import re
from config import CONFIG
NUMBER_QUESTION = "number"
WORD_QUESTION = "word"
BOOLEAN_QUESTION = "(true, false)"

file = open("doc.html", mode="r")
doc = file.read()
file.close()
html = HTML(html=doc)
manual_indexes = []


def gcd(a, b):
    temp = 0
    while not b == 0:
        t = b
        b = a % b
        a = t
    return a


def is_prime(n):
    if n == 2 or n == 3:
        return True
    if n < 2 or n % 2 == 0:
        return False
    if n < 9:
        return True
    if n % 3 == 0:
        return False
    r = int(n**0.5)
    f = 5
    while f <= r:
        if n % f == 0:
            return False
        if n % (f+2) == 0:
            return False
        f += 6
    return True


def extract_question_text(row):
    return row.find("td", first=True).text


def number_question_handler(text):
    match = re.fullmatch(
        "What is the greatest common divisor of ([0-9]+) and ([0-9]+)\?", text)
    if not match:
        return None
    return gcd(int(match.group(1)), int(match.group(2)))


def word_question_handler(text):
    match = re.fullmatch(
        "^What is the ([0-9]+)(?:nd|th|st|rd|) word in the following line: (.+)$", text)
    if not match:
        return None
    index = int(match.group(1))
    line = match.group(2)
    return line.split(" ")[index - 1]


def boolean_question_handler(text):
    match = re.fullmatch("Is ([0-9]+) a prime number\?", text)
    if not match:
        return None
    if is_prime(int(match.group(1))):
        return "true"
    return "false"


QUESTION_HANDLERS = {
    NUMBER_QUESTION: number_question_handler,
    WORD_QUESTION: word_question_handler,
    BOOLEAN_QUESTION: boolean_question_handler,
}

rows = html.find("tbody tr")
output = []

for index, row in enumerate(rows):
    category = row.find("label.active", first=True).text
    if category not in (NUMBER_QUESTION, WORD_QUESTION, BOOLEAN_QUESTION):
        raise ValueError("Invalid category: {}".format(category))
    question_text = extract_question_text(row)
    out = QUESTION_HANDLERS[category](question_text)
    if not out:
        manual_indexes.append(index)
        output.append(question_text)
        continue
    output.append(QUESTION_HANDLERS[category](question_text))

for index in manual_indexes:
    print("#{}: {}".format(index+1, output[index]))
for index in manual_indexes:
    question_text = output[index]
    answer = input("Question #{:0}: {:1} >> ".format(index+1, question_text))
    output[index] = answer

res = requests.post(CONFIG["website_url"], data={
                    "answer": ans for ans in output})
with open("doc.html", mode="w") as file:
    file.write(res.text)
