from flask import Flask, url_for, render_template, abort
from flask.ext.restful import Api, Resource, reqparse
from web.api import get_mps_function
from web.api import get_mp_function
from web.api import get_lords_function
from web.api import get_lord_function
from web.api import get_influencers_function
from web.api import get_influencer_function
from web.api import find_entity_function
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


@app.route('/influencers')
def show_influencers():
    args = {}
    influencers = get_influencers_function.InfluencersApi().request()[1]
    return render_template('show_influencers.html', influencers=influencers)

@app.route('/influencer/<name>')
def show_influencer(name):
    args = {"name": name}
    influencer = get_influencer_function.InfluencerApi().request(args)
    return render_template('show_influencer.html', influencer=influencer)


@app.route('/mps')
def show_mps():
    args = {}
    mps = get_mps_function.MpsApi().request()
    return render_template('show_mps.html', mps=mps)


@app.route('/mp/<name>')
def show_mp(name):
    args = {"name": name}
    mp = get_mp_function.MpApi().request(args)
    return render_template('show_mp.html', mp=mp)


@app.route('/lords')
def show_lords():
    args = {}
    lords = get_lords_function.LordsApi().request()
    return render_template('show_lords.html', lords=lords)


@app.route('/lord/<name>')
def show_lord(name):
    args = {"name": name}
    lord = get_lord_function.LordApi().request(args)
    return render_template('show_lord.html', lord=lord)


class GetMps(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('party', type=str)
        self.reqparse.add_argument('interests_gt', type=int)
        self.reqparse.add_argument('interests_lt', type=int)
        self.reqparse.add_argument('donations_gt', type=int)
        self.reqparse.add_argument('donations_lt', type=int)
        super(GetMps, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_mps_function.MpsApi().request(**args)


class GetMp(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        super(GetMp, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_mp_function.MpApi().request(args)


class GetLords(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('party', type=str)
        self.reqparse.add_argument('donations_gt', type=int)
        self.reqparse.add_argument('donations_lt', type=int)
        super(GetLords, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_lords_function.LordsApi().request(**args)


class GetLord(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        super(GetLord, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_lord_function.LordApi().request(args)


class GetInfluencers(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('labels', type=str)
        self.reqparse.add_argument('interests_gt', type=int)
        self.reqparse.add_argument('interests_lt', type=int)
        self.reqparse.add_argument('donations_gt', type=int)
        self.reqparse.add_argument('donations_lt', type=int)
        super(GetInfluencers, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_influencers_function.InfluencersApi().request(**args)


class GetInfluencer(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        super(GetInfluencer, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_influencer_function.InfluencerApi().request(args)


class FindEntity(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('search', type=str)
        super(FindEntity, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return find_entity_function.EntityApi().request(**args)


api.add_resource(GetMps, '/api/v0.1/getMps', endpoint='getMps')
api.add_resource(GetMp, '/api/v0.1/getMp', endpoint='getMp')
api.add_resource(GetLords, '/api/v0.1/getLords', endpoint='getLords')
api.add_resource(GetLord, '/api/v0.1/getLord', endpoint='getLord')
api.add_resource(GetInfluencers, '/api/v0.1/getInfluencers', endpoint='getInfluencers')
api.add_resource(GetInfluencer, '/api/v0.1/getInfluencer', endpoint='getInfluencer')
api.add_resource(FindEntity, '/api/v0.1/findEntity', endpoint='findEntity')

if __name__ == '__main__':
    app.debug = True
    app.run()
