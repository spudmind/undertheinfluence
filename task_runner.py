# -*- coding: utf-8 -*-
import warnings
warnings.simplefilter("ignore", UserWarning)
import sys
import argparse
import logging

from scrapers import mps, lords, meetings, prca, party_funding

from scrapers import scrape_mps_interests
from scrapers import scrape_lords_interests

from parsers import master_entities
from parsers import parse_mps
from parsers import parse_lords
from parsers import parse_mps_interests
from parsers import parse_lords_interests
from parsers import parse_party_funding

from graphers import graph_mps
from graphers import graph_lords
from graphers import graph_mps_interests
from graphers import graph_lords_interests
from graphers import graph_party_funding

from data_interfaces import api_data_gen
from data_models import core


choices = ["mps", "lords", "mps_interests", "lords_interests", "party_funding", "meetings", "prca"]
arg_parser = argparse.ArgumentParser(description="Task runner for spud.")
arg_parser.add_argument("--verbose", "-v", action="store_true", help="Noisy output")
arg_parser.add_argument("--fetch", nargs="+", choices=choices, help="Specify the fetcher(s) to run")
arg_parser.add_argument("--scrape", nargs="+", choices=choices, help="Specify the scraper(s) to run")
arg_parser.add_argument("--master", nargs="+", choices=["mps", "lords"], help="Parse master entities")
arg_parser.add_argument("--parse", nargs="+", choices=choices, help="Specify the parser(s) to run")
arg_parser.add_argument("--graph", nargs="+", choices=choices, help="Specify the grapher(s) to run")
arg_parser.add_argument("--api_gen", nargs="+", choices=["politicians", "government", "influencers", "parties"], help="Create mongo database for API")
arg_parser.add_argument("--export", nargs="+", choices=["named_entities"], help="Specify the export to run")
args = arg_parser.parse_args()

# if (args.fetch, args.scrape, args.master, args.parse, args.graph, args.export) == (None, None, None, None, None):
#     print "Nothing to do!"
#     arg_parser.print_help()
#     exit()

logger = logging.getLogger("spud")
logger.addHandler(logging.StreamHandler())
if args.verbose:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)

# run fetchers
if args.fetch is not None:
    exec_fetcher = {
        "lords": lords,
        "mps": mps,
        "meetings": meetings,
        "prca": prca,
        "party_funding": party_funding,
    }
    for fetcher in args.fetch:
        exec_fetcher[fetcher].fetch()

# run scrapers
if args.scrape is not None:
    exec_scraper = {
        "mps": mps,
        "lords": lords,
        "mps_interests": scrape_mps_interests.MPsInterestsScraper,
        "lords_interests": scrape_lords_interests.LordsInterestsScraper,
        "party_funding": party_funding,
        "meetings": meetings,
        "prca": prca,
    }
    for scraper in args.scrape:
        exec_scraper[scraper].scrape()

# parse master entities
if args.master is not None:
    master = master_entities.MasterEntitiesParser()
    if "mps" in args.master:
        master.create_mps()
    if "lords" in args.master:
        master.create_lords()

# run parsers
if args.parse is not None:
    exec_parser = {
        "mps": parse_mps.MPsParser,
        "lords": parse_lords.LordsParser,
        "mps_interests": parse_mps_interests.MPsInterestsParser,
        "lords_interests": parse_lords_interests.LordsInterestsParser,
        "party_funding": parse_party_funding.PartyFundingParser,
    }
    for parser in args.parse:
        exec_parser[parser]().run()

# run graphers
if args.graph is not None:
    exec_grapher = {
        "mps": graph_mps.GraphMPs,
        "lords": graph_lords.GraphLords,
        "mps_interests": graph_mps_interests.GraphMPsInterests,
        "lords_interests": graph_lords_interests.GraphLordsInterests,
        "party_funding": graph_party_funding.GraphPartyFunding,
    }
    for grapher in args.graph:
        exec_grapher[grapher]().run()

# populate node stat lists for api
if args.api_gen is not None:
    if "politicians" in args.api_gen:
        api_data_gen.PopulatePoliticiansApi().run()
        api_data_gen.PopulateMpsApi().run()
        api_data_gen.PopulateLordsApi().run()
    if "influencers" in args.api_gen:
        api_data_gen.PopulateInfluencersApi().run()
    if "government" in args.api_gen:
        api_data_gen.PopulateDepartmentsApi().run()
    if "parties" in args.api_gen:
        api_data_gen.PopulatePoliticalPartyApi().run()


# run export
if args.export is not None:
    model = core.BaseDataModel()
    if "named_entities" in args.export:
        model.named_entity_export()

