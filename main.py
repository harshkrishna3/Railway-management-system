from flask import Flask, request
from flask_restful import Api, Resource
import json
from railway_management_api import RailwayManagement

app = Flask(__name__)
api = Api(app)

class LogIn(Resource):
    def put(self):
        # vals = json.loads(request.form)
        vals = request.form
        try:
            railway = RailwayManagement(vals['user'], vals['password'])
            railway.log_in()
            return {'msg': 'success'}, 200
        except AttributeError:
            return {'msg': 'error'}, 401

class SignUp(Resource):
    def put(self):
        vals = request.form
        try:
            railway = RailwayManagement('rail_api', 'railpassword')
            vals = request.form
            try:
                email = vals['email']
            except KeyError:
                email = None
            try:
                address = vals['add']
            except KeyError:
                address = None
            railway.sign_up(vals['user'], vals['password'], vals['name'], vals['dob'], vals['mob'], email, address)
            return {'msg': 'success'}, 201
        except Exception as e:
            print(e)
            return {'msg': 'error'}, 500

class CheckPnr(Resource):
    def get(self, pnr):
        railway = RailwayManagement('guest', 'guest')
        ticket = railway.check_pnr(pnr)
        ticket['coach'] = ticket['seat_sqn']//72
        ticket['seat'] = ticket['seat_sqn']%72
        del ticket['seat_sqn']
        return ticket

class Route(Resource):
    def get(self, train_no):
        railway = RailwayManagement('guest', 'guest')
        train = railway.show_train_details(train_no)
        return train

class SeatAvaiibilty(Resource):
    def put(self):
        vals = request.form
        railway = RailwayManagement('guest', 'guest')
        aval_seat = railway.seat_availability(vals['stn_frm'], vals['stn_to'], vals['train_no'], vals['travel_date'])
        return aval_seat

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
        

api.add_resource(LogIn, '/login')
api.add_resource(SignUp, '/signup')
api.add_resource(CheckPnr, '/pnr/<int:pnr>')
api.add_resource(Route, '/route/<int:train_no>')
api.add_resource(SeatAvaiibilty, '/seat-availibility')
api.add_resource(TrainBwStations, '/train-bw-stations/<string:frm>/<string:to>')
api.add_resource(BookTicket, '/book')

if __name__ == '__main__':
    app.run(debug=True)