from scrapers import mps as fetch_mps
from scrapers import members_interests
from scrapers import lords_interests
from scrapers import party_funding
from scrapers import lords
from parsers import master_entities
from parsers import mps as parse_mp_info
from parsers import members_interests as interests_parse
from parsers import party_funding as funding_parse
from parsers import lords as lords_parse
from graphers import mps as mp_import
from graphers import members_interests as interests_graph
from graphers import party_funding as funding_graph
from graphers import lords as lords_graph

# from parsers import master_entities
# parse_master = master_entities.MasterEntitiesParser()
# parse_master.create_lords()

#get_members_interests = members_interests.MembersInterestsScraper()
#get_lords_interests = lords_interests.LordsInterestsScraper()
#get_lords = lords.LordsInfoScaper()
#get_funding = party_funding.PartyFundingScaper()
#get_mps = mps.MpInfoScaper()
#get_members_interests.run()
#get_lords_interests.run()
#get_lords.run()
#get_funding.run()
#get_mps.run()


#parse_master = master_entities.MasterEntitiesParser()
#parse_mps = parse_mp_info.MpsParser()
#parse_lords = lords_parse.LordsParser()
parse_interests = interests_parse.MembersInterestsParser()
party_parse = funding_parse.PartyFundingParser()
#parse_master.create_lords()
#parse_mps.run()
#parse_lords.run()
parse_interests.run()
party_parse.run()

#graph_mps = mp_import.GraphMPs()
#graph_lords = lords_graph.GraphLords()
#graph_interests = interests_graph.GraphMembersInterests()
#graph_party_funding = funding_graph.GraphPartyFunding()
#graph_mps.run()
#graph_lords.run()
#graph_interests.run()
#graph_party_funding.run()
