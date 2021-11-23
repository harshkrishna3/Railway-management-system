import mysql.connector
from datetime import date
class RailwayManagement:
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.host = 'localhost'
        self.database = 'railway_management_system'

    def _connectDB(self):
        self.db = mysql.connector.connect(
            host = self.host,
            user = self.user,
            password = self.password,
            database = self.database
        )
        return self.db.cursor(buffered = True)

    def _closeDB(self):
        self.db.close()

    def show_train_details(self, train_no):
        try:
            csr = self._connectDB()
            csr.execute('select * from trains where train_no = {0}'.format(train_no))
            details = csr.fetchone()
            all_details = {'train_no': details[0], 'name': details[1], 'total_coach': details[2], 'running_days': details[3]}
            csr.execute('select * from time_table where train_no = 12309 order by day_no, ifnull(arrival, departure) + ifnull(departure, arrival)')
            all_details['time_table'] = csr.fetchall()
            return all_details

        finally:
            self._closeDB()

    def train_bw_stations(self, station_frm, station_to):
        try:
            pot_trains = list()
            csr = self._connectDB()
            csr.execute('''
                select distinct * from
                (select train_no from time_table where stn_code = '{0}') query1
                inner join
                (select train_no from time_table where stn_code = '{1}') query2
                using (train_no)
            '''.format(station_frm, station_to))
            all_trains = csr.fetchall()
            for train_num in all_trains:
                train = train_num[0]
                csr.execute("select departure, day_no from time_table where train_no = '{0}' and stn_code = '{1}'".format(train, station_frm))
                departure, day_no_from = csr.fetchone()
                csr.execute("select arrival, day_no from time_table where train_no = '{0}' and stn_code = '{1}'".format(train, station_to))
                arrival, day_no_to = csr.fetchone()
                if (day_no_from, departure) < (day_no_to, arrival):
                    train_info = dict()
                    csr.execute('select name from trains where train_no = {0}'.format(train))
                    train_info['train_no'] = train
                    train_info['name'] = csr.fetchone()
                    train_info['arrival'] = arrival
                    train_info['day_no_frm'] = day_no_from
                    train_info['departure'] = departure
                    train_info['day_no_to'] = day_no_to
                    pot_trains.append(train_info)
            return pot_trains
        finally:
            self._closeDB()

    def _train_runs_on_day(self, travel_date, days):
        day = date.fromisoformat(travel_date).weekday()
        return bool(int(days[day]))

    def seat_availability(self, station_frm, station_to, train_no, travel_date):
            try:
                csr = self._connectDB()
                csr.execute('select total_coach, days from trains where train_no = {0}'.format(train_no))
                total_coach, days = csr.fetchone()
                if not self._train_runs_on_day(travel_date, days):
                    raise ValueError('Train doesnt run on entered day')
                csr.execute("select stn_code from time_table where train_no = {0}".format(train_no))
                stations = list(map(lambda x:x[0], csr.fetchall()))
                for i, stn in enumerate(stations):
                    if stn == station_frm:
                        start = i
                    if stn == station_to:
                        end = i
                        break
                stations = stations[start:end+1]
                filled_seats = list()
                for stn in stations:
                    csr.execute("select count(*) from seat_booked where train_no = {0} and travel_date = '{1}' and stn_code = '{2}'".format(train_no, travel_date, stn))
                    filled_seats.append(csr.fetchone()[0])
                return total_coach*72 - max(filled_seats)

            finally:
                self._closeDB()


