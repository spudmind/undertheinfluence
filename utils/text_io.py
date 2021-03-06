class MetricsOutput:
    def __init__(self):
        self.csv_header = \
            "words_total," \
            "words_unique," \
            "words_diversity," \
            "word_per_sent," \
            "sentiment_total," \
            "sentiment_mean," \
            "pos_sentiments," \
            "neg_sentiments," \
            "neu_sentiments," \
            "subjectivity_total," \
            "subjectivity_mean," \
            "named_entity_count," \
            "named_entity_unique," \
            "statement_count," \
            "relations_unique," \
            "noun_phrase_count," \
            "noun_phrase_unique," \
            "nounphrase_common," \
            "link"
        self.csv_output = open('document_metrics.csv', 'w')
        self.csv_output.write(self.csv_header + "\n")
        self.document_data = {}

    def write_to_csv(self):
        line = ""
        for field in self.csv_header.split(","):
            if line == "":
                line = str(self.document_data[field])
            else:
                line += "," + str(self.document_data[field])
        self.csv_output.write(line + "\n")
