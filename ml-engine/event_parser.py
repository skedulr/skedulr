from transformers import BertForQuestionAnswering
from transformers import BertTokenizer
from bert import bert_feature_extraction
from handler import operation_handler, name_handler, location_handler, summary_handler, date_handler
import spacy
import re
from datetime import datetime, timedelta


def meeting_details_parse(message, contact_list):
    model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    nlp = spacy.load('en_core_web_md')

    compiled = re.compile(re.escape("today"), re.IGNORECASE)
    message = compiled.sub(str(datetime.today()).split(' ')[0], message)

    compiled = re.compile(re.escape("now"), re.IGNORECASE)
    message = compiled.sub(str(datetime.today()).split(' ')[0], message)

    compiled = re.compile(re.escape("tomorrow"), re.IGNORECASE)
    message = compiled.sub(str(datetime.today() + timedelta(days=1)).split(' ')[0], message)

    dates = date_handler(message, nlp, model, tokenizer)

    return {
        "operation": operation_handler(message, nlp),
        "location": location_handler(message, model, tokenizer),
        "attendees": name_handler(message, nlp, model, tokenizer, contact_list),
        "summary": summary_handler(message, model, tokenizer),
        "start_date": dates[0],
        "end_date": dates[1],
    }
