from flask import Flask, render_template, request
from flask.ext.restful import Api, Resource, reqparse
from web.api import get_summary_function
from web.api import get_mp_function
from web.api import get_lord_function
from web.api import get_influencers_function
from web.api import get_influencer_function
from web.api import get_parties_function
from web.api import get_party_function
from web.api import get_politicians_function
from web.api import get_departments_function
from web.api import get_lobbyists_function
from web.api import find_entity_function
from web.api import get_summary_data
import os

template_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'web/templates'
)
static_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'web/static'
)
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(__name__)
api = Api(app)


@app.route('/')
def show_summary():
    summary = get_summary_function.SummaryApi().request()['results']["summary"]
    return render_template('show_summary.html', summary=summary)


@app.route('/search', methods=['POST'])
def show_search_result():
    search = request.form['search']
    args = {"search": search}
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    results = find_entity_function.EntityApi().request(args)['results']
    return render_template(
        'show_search_results.html', search_string=search, results=results, page=page
    )


@app.route('/about')
def show_about():
    return render_template('show_about.html')


@app.route('/contact')
def show_contact():
    return render_template('show_contact.html')


@app.route('/politicians')
def show_politicians():
    args = {}
    reply = get_summary_function.SummaryApi().request()
    mps_summary = reply["results"]["summary"]["mps"]
    lords_summary = reply["results"]["summary"]["lords"]
    return render_template(
        'politicians_summary.html', mps=mps_summary, lords=lords_summary)

@app.route('/politicians/detail')
def show_politicians_detail():
    args = {}
    title = None
    args["page"] = int(request.args.get('page', 1))
    args["government_department"] = request.args.get('government_department', None)
    if args["government_department"]:
        title = args["government_department"]
    reply = get_politicians_function.PoliticiansApi().request(**args)
    politicians, pager = reply['results'], reply['pager']
    return render_template(
        'politicians_detail.html', politicians=politicians, pager=pager, title=title
    )


@app.route('/lobbyists')
def show_lobbyists():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    lobbyists = get_lobbyists_function.LobbyistsApi().request(page=page)['results']
    return render_template('show_lobbyists.html', lobbyists=lobbyists, page=page)


@app.route('/influencers')
def show_influencers():
    args = {}
    args["labels"] = request.args.get('labels', None)
    reply = get_summary_function.SummaryApi().request()
    influencer_summary = reply["results"]["summary"]["influencers"]
    return render_template('influencers_summary.html', influencers=influencer_summary)


@app.route('/influencers/detail')
def show_influencers_detail():
    args = {}
    title = None
    args["page"] = int(request.args.get('page', 1))
    args["labels"] = request.args.get('labels', None)
    if args["labels"]:
        title = args["labels"]
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    reply = get_influencers_function.InfluencersApi().request(**args)
    influencers, pager = reply['results'], reply['pager']
    return render_template(
        'influencers_detail.html', influencers=influencers, page=page, title=title
    )


@app.route('/influencer/<name>')
def show_influencer(name):
    args = {"name": name}
    influencer = get_influencer_function.InfluencerApi().request(args)
    return render_template('show_influencer.html', influencer=influencer)


@app.route('/mp/<name>')
def show_mp(name):
    args = {"name": name}
    mp = get_mp_function.MpApi().request(args)
    return render_template('show_mp.html', mp=mp)


@app.route('/lord/<name>')
def show_lord(name):
    args = {"name": name}
    lord = get_lord_function.LordApi().request(args)
    return render_template('show_lord.html', lord=lord)


@app.route('/parties/')
def show_parties():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    parties = get_parties_function.PoliticalPartiesApi().request(page=page)['results']
    return render_template('show_parties.html', parties=parties, page=page)


@app.route('/party/<name>')
def show_party(name):
    args = {"name": name}
    party = get_party_function.PoliticalPartyApi().request(args)
    return render_template('show_party.html', party=party)


@app.route('/committees/')
def show_committees():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    offices = get_departments_function.DepartmentsApi().request(page=page)['results']
    return render_template('show_committees.html', offices=offices, page=page)


class GetSummary(Resource):
    def __init__(self):
        super(GetSummary, self).__init__()

    def get(self):
        return get_summary_function.SummaryApi().request()


class GetPoliticians(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('page', type=int)
        self.reqparse.add_argument('party', type=str)
        self.reqparse.add_argument('type', type=str)
        self.reqparse.add_argument('government_department', type=str)
        self.reqparse.add_argument('interests_gt', type=int)
        self.reqparse.add_argument('interests_lt', type=int)
        self.reqparse.add_argument('donations_gt', type=int)
        self.reqparse.add_argument('donations_lt', type=int)
        super(GetPoliticians, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        # set a default for 'page'
        args['page'] = (args['page'], 1)[args['page'] is None]

        return get_politicians_function.PoliticiansApi().request(**args)


class GetMp(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        super(GetMp, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_mp_function.MpApi().request(args)


class GetLord(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        super(GetLord, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_lord_function.LordApi().request(args)


class GetPoliticalParties(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('page', type=int)
        super(GetPoliticalParties, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        # set a default for 'page'
        args['page'] = (args['page'], 1)[args['page'] is None]

        return get_parties_function.PoliticalPartiesApi().request(**args)


class GetPoliticalParty(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        super(GetPoliticalParty, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_party_function.PoliticalPartyApi().request(args)


class GetLobbyists(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('page', type=int)
        self.reqparse.add_argument('name', type=str)
        super(GetLobbyists, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        # set a default for 'page'
        args['page'] = (args['page'], 1)[args['page'] is None]
        # print "args:", args
        return get_lobbyists_function.LobbyistsApi().request(**args)


class GetInfluencers(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('page', type=int)
        self.reqparse.add_argument('labels', type=str)
        self.reqparse.add_argument('interests_gt', type=int)
        self.reqparse.add_argument('interests_lt', type=int)
        self.reqparse.add_argument('donations_gt', type=int)
        self.reqparse.add_argument('donations_lt', type=int)
        self.reqparse.add_argument('lobbyists_gt', type=int)
        self.reqparse.add_argument('lobbyists_lt', type=int)
        super(GetInfluencers, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        # set a default for 'page'
        args['page'] = (args['page'], 1)[args['page'] is None]
        # print "args:", args
        return get_influencers_function.InfluencersApi().request(**args)


class GetInfluencer(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        super(GetInfluencer, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_influencer_function.InfluencerApi().request(args)


class GetGovernmentDepartments(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        super(GetGovernmentDepartments, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_departments_function.DepartmentsApi().request()


class FindEntity(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('search', type=str)
        super(FindEntity, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return find_entity_function.EntityApi().request(args)


class GetData(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('type', type=str)
        self.reqparse.add_argument('category', type=str)
        self.reqparse.add_argument('field', type=str)
        super(GetData, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_summary_data.DataApi().request(**args)



api.add_resource(GetSummary, '/api/v0.1/', endpoint='getSummary')
api.add_resource(GetPoliticians, '/api/v0.1/getPoliticians', endpoint='getPoliticians')
api.add_resource(GetMp, '/api/v0.1/getMp', endpoint='getMp')
api.add_resource(GetLord, '/api/v0.1/getLord', endpoint='getLord')
api.add_resource(GetInfluencers, '/api/v0.1/getInfluencers', endpoint='getInfluencers')
api.add_resource(GetInfluencer, '/api/v0.1/getInfluencer', endpoint='getInfluencer')
api.add_resource(GetLobbyists, '/api/v0.1/getLobbyAgencies', endpoint='getLobbyAgencies')
api.add_resource(GetPoliticalParties, '/api/v0.1/getPoliticalParties', endpoint='getPoliticalParties')
api.add_resource(GetPoliticalParty, '/api/v0.1/getPoliticalParty', endpoint='getPoliticalParty')
api.add_resource(GetGovernmentDepartments, '/api/v0.1/getGovernmentDepartments', endpoint='getGovernmentDepartments')
api.add_resource(FindEntity, '/api/v0.1/findEntity', endpoint='findEntity')
api.add_resource(GetData, '/api/v0.1/data', endpoint='data')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
