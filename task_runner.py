import argparse

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

# master_entities.MasterEntitiesParser().create_mps()
# master_entities.MasterEntitiesParser().create_lords()

# from data_interfaces import api
# from data_models import core

# dump = core.BaseDataModel()
# dump.named_entity_export()

# mps_api = api.PopulateMpsApi()
# mps_api.run()

choices = ['mps', 'lords', 'mps_interests', 'lords_interests', 'party_funding']
arg_parser = argparse.ArgumentParser(description='Task runner for spud.')
arg_parser.add_argument('--scrape', nargs='+', choices=choices, help='Specify the scraper(s) to run')
arg_parser.add_argument('--parse', nargs='+', choices=choices, help='Specify the parser(s) to run')
arg_parser.add_argument('--graph', nargs='+', choices=choices, help='Specify the grapher(s) to run')
args = arg_parser.parse_args()

if (args.scrape, args.parse, args.graph) == (None, None, None):
    print 'Nothing to do!'
    arg_parser.print_help()
    exit()

# run scrapers
if args.scrape is not None:
    exec_scraper = {
        'mps': scrape_mps.MPsInfoScraper(),
        'lords': scrape_lords.LordsInfoScraper(),
        'mps_interests': scrape_mps_interests.MPsInterestsScraper(),
        'lords_interests': scrape_lords_interests.LordsInterestsScraper(),
        'party_funding': scrape_party_funding.PartyFundingScaper(),
    }
    for scraper in args.scrape:
        exec_scraper[scraper].run()

# run parsers
if args.parse is not None:
    exec_parser = {
        'mps': parse_mps.MPsParser(),
        'lords': parse_lords.LordsParser(),
        'mps_interests': parse_mps_interests.MPsInterestsParser(),
        'lords_interests': parse_lords_interests.LordsInterestsParser(),
        'party_funding': parse_party_funding.PartyFundingParser(),
    }
    for parser in args.parse:
        exec_parser[scraper].run()

# run graphers
if args.graph is not None:
    exec_grapher = {
        'mps': graph_mps.GraphMPs(),
        'lords': graph_lords.GraphLords(),
        'mps_interests': graph_mps_interests.GraphMPsInterests(),
        # 'lords_interests': graph_lords_interests.GraphLordsInterests(),
        'party_funding': graph_party_funding.GraphPartyFunding(),
    }
    for grapher in args.graph:
        exec_grapher[grapher].run()
