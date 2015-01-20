from scrapers import mps as fetch_mps
from scrapers import party_funding
from scrapers import lords
from parsers import master_entities
from parsers import mps as parse_mp_info
from parsers import members_interests
from parsers import lords as lords_parse
from graphers import mps as mp_import
from graphers import members_interests as members_import
from graphers import party_funding
from graphers import lords as lords_graph


#get_lords = lords.LordsInfoScaper()
#get_funding = party_funding.PartyFundingScaper()
#get_mps = mps.MpInfoScaper()
#get_lords.run()
#get_funding.run()
#get_mps.run()

#parse_mps = parse_mp_info.MpsParser()
#parse_lords = lords_parse.LordsParser()
#parse_interests = members_interests.MembersInterestsParser()
#parse_master = master_entities.MasterEntitiesParser()
#party_parse = party_funding.PartyFundingParser()
#parse_mps.run()
#parse_lords.run()
#parse_master.create_lords()
#parse_interests.run()
#party_parse.run()

#graph_mps = mp_import.GraphMPs()
graph_lords = lords_graph.GraphLords()
#graph_interests = members_import.GraphMembersInterests()
#graph_party_funding = party_funding.GraphPartyFunding()
#graph_mps.run()
graph_lords.run()
#graph_interests.run()
#graph_party_funding.run()