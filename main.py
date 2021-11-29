from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
from railway_management_api import RailwayManagement

app = Flask(__name__)
api = Api(app)
CORS(app)

class LogIn(Resource):
    def get(self, user, password):
        # vals = json.loads(request.form)
        # vals = request.form
        try:
            railway = RailwayManagement(user, password)
            railway.log_in()
            return {'msg': 'success'}, 200
        except AttributeError:
            return {'msg': 'error'}, 401

# @app.route('/')
class SignUp(Resource):
    def get(self, user, password, name, dob, mob, email=None, address=None):
        # vals = request.form
        try:
            railway = RailwayManagement('rail_api', 'railpassword')
            vals = request.form
            # try:
            #     email = vals['email']
            # except KeyError:
            #     email = None
            # try:
            #     address = vals['add']
            # except KeyError:
            #     address = None
            railway.sign_up(user, password, name, dob, mob, email, address)
            return {'msg': 'success'}, 201
        except Exception as e:
            print(e)
            return {'msg': 'error'}, 500

class CheckPnr(Resource):
    def get(self, pnr):
        railway = RailwayManagement('guest', 'guest')
        ticket = railway.check_pnr(pnr)
        print(type(ticket))
        ticket['coach'] = ticket['seat_sqn']//72 +1
        ticket['seat'] = ticket['seat_sqn']%72
        del ticket['seat_sqn']
        return ticket, 200

class Route(Resource):
    def get(self, train_no):
        railway = RailwayManagement('guest', 'guest')
        train = railway.show_train_details(train_no)
        # print(train)
        return train

# @app.route('/')
class SeatAvaiibilty(Resource):
    def get(self, frm, to, train_no, travel_date):
        vals = request.form
        # print(vals['stn_frm'])
        railway = RailwayManagement('guest', 'guest')
        aval_seat = railway.seat_availability(frm, to, train_no, travel_date)
        return {'avail': aval_seat}

class TrainBwStations(Resource):
    def get(self, frm, to):
        railway = RailwayManagement('guest', 'guest')
        stations = railway.train_bw_stations(frm, to)
        return stations

class BookTicket(Resource):
    def put(self):
        vals = request.form
        railway = RailwayManagement(vals['user'], vals['psw'])
        pnr, seat_sqn = railway.book_ticket(vals['psg_name'], vals['frm'], vals['to'], vals['travel_date'], vals['train_no'])
        return {'pnr': pnr, 'coach': seat_sqn//72, 'seat': seat_sqn%72}, 201
        

api.add_resource(LogIn, '/login/<string:user>/<string:password>')
api.add_resource(SignUp, '/signup/<string:user>/<string:password>/<string:name>/<string:dob>/<string:mob>/<string:email>/<string:address>')
api.add_resource(CheckPnr, '/pnr/<int:pnr>')
api.add_resource(Route, '/route/<int:train_no>')
api.add_resource(SeatAvaiibilty, '/seat-availibility/<string:frm>/<string:to>/<string:train_no>/<string:travel_date>')
api.add_resource(TrainBwStations, '/train-bw-stations/<string:frm>/<string:to>')
api.add_resource(BookTicket, '/book')

if __name__ == '__main__':
    app.run(debug=True)