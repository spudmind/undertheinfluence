from scrapers import scrape_mps
from scrapers import scrape_lords
from scrapers import scrape_mps_interests
from scrapers import scrape_lords_interests
from scrapers import scrape_party_funding

from parsers import master_entities
from parsers import parse_mps
from parsers import parse_lords
from parsers import parse_mps_interests
from parsers import parse_lords_interests
from parsers import parse_party_funding

from graphers import graph_mps
from graphers import graph_lords
from graphers import graph_mps_interests
from graphers import graph_party_funding

from data_interfaces import api
from data_models import core

dump = core.BaseDataModel()
dump.named_entity_export()

#mps_api = api.PopulateMpsApi()
#mps_api.run()

# scrape_mps.MPsInfoScraper().run()
# scrape_lords.LordsInfoScraper().run()
# scrape_mps_interests.MPsInterestsScraper().run()
# scrape_lords_interests.LordsInterestsScraper().run()
# scrape_party_funding.PartyFundingScraper().run()

# master_entities.MasterEntitiesParser().create_mps()
# master_entities.MasterEntitiesParser().create_lords()
# parse_mps.MPsParser().run()
# parse_lords.LordsParser().run()
# parse_mps_interests.MPsInterestsParser().run()
# parse_lords_interests.LordsInterestsParser().run()
# parse_party_funding.PartyFundingParser().run()

# graph_mps.GraphMPs().run()
# graph_lords.GraphLords().run()
# graph_mps_interests.GraphMPsInterests().run()
# graph_party_funding.GraphPartyFunding().run()
