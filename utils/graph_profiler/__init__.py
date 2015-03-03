from data_models import government
from data_models import core


class DataProfiler:
    def __init__(self):
        self.data_models = government
        self.core_model = core.BaseDataModel()
        self.node_types = [
            "Named Entity",
            "Member of Parliament",
            "Donor",
            "Donation Recipient",
            "Elected Term",
            "Government Office",
            "Political Party",
            "Interest Category",
            "Funding Relationship",
            "Registered Funding",
            "Registered Interest",
            "Remuneration",
        ]