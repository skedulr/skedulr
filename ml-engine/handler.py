import spacy
from fuzzywuzzy import fuzz
import re
from bert import bert_feature_extraction
from datetime import datetime, timedelta
from dateutil.parser import parse
from word2number import w2n


def word_similarity(nlp, w1, w2):
    tokens = nlp("{} {}".format(w1, w2))
    return tokens[0].similarity(tokens[1])


def name_matching(n1, n2):
    if n1 is None or n2 is None:
        return 0
    return fuzz.ratio(n1.lower(), n2.lower())


def operation_handler(text, nlp):
    text_pos = nlp(text)

    op = "create"
    for token in text_pos:
        if str(token.pos_) == "VERB" or str(token.pos_) == "ADJ":
            create_prob = max(word_similarity(nlp, "create", str(token)), word_similarity(nlp, "schedule", str(token)))
            delete_prob = word_similarity(nlp, "delete", str(token))

            if create_prob > 0.2 or delete_prob > 0.2:
                if create_prob > delete_prob:
                    op = "create"
                else:
                    op = "delete"
            break

    return op


def name_handler(text, nlp, model, tokenizer, contact_list):
    res = bert_feature_extraction(model, tokenizer, "who will attend", text)
    print(res)

    if name_matching(res, text) > 60:
        return []

    text_pos = nlp(res)

    attendees = []
    tmp_text_pos = str(text_pos)
    for token in text_pos:
        if str(token.pos_) in ["CCONJ", "PUNCT"]:
            attendee = tmp_text_pos.split(str(token))[0]
            attendees.append(attendee)
            tmp_text_pos = tmp_text_pos.replace(attendee, "")
            tmp_text_pos = tmp_text_pos.replace(str(token), "").strip()

    if tmp_text_pos != "":
        attendees.append(tmp_text_pos)

    final_attendees = []
    for i in range(len(attendees)):
        best_score = 0
        best_match = None
        for contact in contact_list:
            if best_score < name_matching(contact["name"], attendees[i]):
                best_score = name_matching(contact["name"], attendees[i])

                best_match = contact
        if best_match is not None and best_score > 10:
            final_attendees.append(best_match)
            contact_list = list(filter(lambda x: x["name"] != best_match["name"], contact_list))
    return final_attendees


def location_handler(text, model, tokenizer):
    res = bert_feature_extraction(model, tokenizer, "where is meeting", text)

    # failure case
    if name_matching(res, text) > 60 or len(res) > 30:
        return None
    return res


def summary_handler(text, model, tokenizer):
    res = bert_feature_extraction(model, tokenizer, "What is the meeting for", text)

    # failure case
    if name_matching(res, text) > 60 or len(res) > 50:
        return None
    return res


def summary_handler(text, model, tokenizer):
    res = bert_feature_extraction(model, tokenizer, "What is the meeting topic", text)
    # failure case
    if name_matching(res, text) > 60 or len(res) > 50:
        return None

    return res


def replace_all(pattern, repl, string) -> str:
    occurences = re.findall(pattern, string, re.IGNORECASE)
    for occurence in occurences:
        string = string.replace(occurence, repl)
        return string


def date_handler(text, nlp, model, tokenizer):

    res = bert_feature_extraction(model, tokenizer, "which date is the meeting", text)

    if name_matching(res, text) > 60 or len(res) > 50:
        return (None, None)

    res2 = bert_feature_extraction(model, tokenizer, "how much time after", text)

    if name_matching(res2, text) > 60 or len(res2) > 50:

        start_date_obj = parse(res)
        end_date_obj = start_date_obj + timedelta(days=1)
    else:
        tagged_text = nlp(res2)
        isDay = False
        isMonth = False
        isYear = False
        for word in tagged_text:
            if str(word.pos_) == "NUM":
                delta = w2n.word_to_num(str(word))
            else:
                if str(word) == "days":
                    isDay = True
                elif str(word) == "months":
                    isMonth = True
                elif str(word) == "years":
                    isYear = True
                elif str(word) == "weeks":
                    isDay = True
                    delta = delta * 7

        if isDay:
            start_date_obj = parse(res) + timedelta(days=delta)
        elif isMonth:
            start_date_obj = parse(res) + timedelta(months=delta)
        elif isYear:
            start_date_obj = parse(res) + timedelta(years=delta)
        else:
            start_date_obj = parse(res)

    end_date_obj = start_date_obj + timedelta(days=1)

    return (start_date_obj.isoformat(), end_date_obj.isoformat())
