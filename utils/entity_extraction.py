#!/usr/bin/python
import sys
import os
parent = os.path.dirname(os.path.realpath(__file__))

sys.path.append(parent + '/../../mitielib')
from mitie.mit_ie_interface import *

class NamedEntityExtractor:
    SYSTEM_PATH = os.path.dirname(os.path.realpath(__file__))
    MIT_NLP = '/mitie/'
    NE_MODELS = "MITIE-models/english/ner_model.dat"
    NE_DATA = SYSTEM_PATH + MIT_NLP + NE_MODELS

    def __init__(self):
        self.extractor = named_entity_extractor(NamedEntityExtractor.NE_DATA)
        self.tokenizer = tokenize

    def get_entities(self, text):
        entities_text = []
        ascii_test = text.encode('utf8')
        tokens = self.tokenizer(ascii_test)
        #tokens = self.tokenizer(text)
        entities = self.extractor.extract_entities(tokens)
        for e in entities:
            range = e[0]
            tag = e[1]
            entity_text = u" ".join(tokens[i].decode('utf-8') for i in range)
            if not u'"' in entity_text:
                entities_text.append(entity_text)
        if len(entities_text) < 1:
            return None
        else:
            return entities_text



