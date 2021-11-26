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

    def log_in(self):
        try:
            csr = self._connectDB()
            # abc = self.db
        finally:
            self._closeDB()

    def sign_up(self, user, psw, name, dob, mob, email = None, address = None):
        try:
            csr = self._connectDB()
            fields = ['username', 'password', 'name', 'dob', 'mobile']
            values = [user, psw, name, dob, mob]
            if email is not None:
                fields.append('email')
                values.append(email)
            if address is not None:
                fields.append('address')
                values.append(address)
            csr.execute("create user '{0}'@'localhost' identified by '{1}'".format(user, psw))
            csr.execute('insert into User ({0}) values ({1})'.format(', '.join(fields), ', '.join(map(lambda x: '\''+x+'\'', values))))
            self.db.commit()

        finally:
            self._closeDB()

    def show_train_details(self, train_no):
        try:
            csr = self._connectDB()
            csr.execute('select * from trains where train_no = {0}'.format(train_no))
            details = csr.fetchone()
            all_details = {'train_no': details[0], 'name': details[1], 'total_coach': details[2], 'running_days': details[3]}
            csr.execute('select * from time_table where train_no = 12309 order by day_no, ifnull(arrival, departure) + ifnull(departure, arrival)')
            time_table_temp = csr.fetchall()
            all_details['time_table'] = []
            for row in time_table_temp:
                try:
                    arrival = str(row[2])
                except AttributeError:
                    arrival = None
                try:
                    departure = str(row[3])
                except AttributeError:
                    departure = None
                all_details['time_table'].append((*row[0:2], arrival, departure, row[4:]))
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
                    train_info['arrival'] = str(arrival)
                    train_info['day_no_frm'] = day_no_from
                    train_info['departure'] = str(departure)
                    train_info['day_no_to'] = day_no_to
                    pot_trains.append(train_info)
            return pot_trains
        finally:
            self._closeDB()

    def _train_runs_on_day(self, travel_date, days):
        day = date.fromisoformat(travel_date).weekday()
        return bool(int(days[day]))
    
    def check_pnr(self, pnr):
        try:
            csr = self._connectDB()
            csr.execute("select * from ticket where pnr = {0}".format(pnr))
            ticket = dict()
            _, ticket['booked_by'], ticket['psg_name'] = csr.fetchone()
            csr.execute("select stn_code from seat_booked where pnr = {0}".format(pnr))
            stations = list(map(lambda x:x[0], csr.fetchall()))
            csr.execute("select distinct seat_sqn, travel_date, train_no from seat_booked where pnr = {0}".format(pnr))
            ticket['seat_sqn'], ticket['travel_date'], ticket['train_no'] = csr.fetchone()
            ticket['travel_date'] = ticket['travel_date'].isoformat()
            csr.fetchall()
        finally:
            self._closeDB()
        stn_visited_by_train = list(map(lambda x:x[0], self.show_train_details(ticket['train_no'])['time_table']))
        stations.sort(key= lambda x:stn_visited_by_train.index(x))
        ticket['first_stn'] = stations[0]
        ticket['last_stn'] = stn_visited_by_train[stn_visited_by_train.index(stations[-1])+1]
        return ticket, 200


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
                stations = stations[start:end]
                filled_seats = list()
                for stn in stations:
                    csr.execute("select count(*) from seat_booked where train_no = {0} and travel_date = '{1}' and stn_code = '{2}'".format(train_no, travel_date, stn))
                    filled_seats.append(csr.fetchone()[0])
                return total_coach*72 - max(filled_seats)

            finally:
                self._closeDB()

    def book_ticket(self, psg_name, stn_frm, stn_to, travel_date, train_no):
        if self.seat_availability(stn_frm, stn_to, train_no, travel_date) < 0:
            raise ValueError('No available seats in the train')
        try:
            csr = self._connectDB()
            csr.execute("insert into ticket(booked_by, psg_name) values('{0}', '{1}')".format(self.user, psg_name))
            self.db.commit()
            csr.execute('select last_insert_id()')
            pnr = csr.fetchone()[0]


            csr.execute("select stn_code from time_table where train_no = {0}".format(train_no))
            stations = list(map(lambda x:x[0], csr.fetchall()))
            for i, stn in enumerate(stations):
                if stn == stn_frm:
                    start = i
                if stn == stn_to:
                    end = i
                    break
            stations = stations[start:end]
            
            #get suitable seat_sqn for most efficiency
            csr.execute("select count(*), seat_sqn from seat_booked where train_no = '{0}' and travel_date = '{1}' group by seat_sqn having seat_sqn not in (select distinct seat_sqn from seat_booked where stn_code in ({2}))".format(train_no, travel_date, ', '.join(map(lambda x: "'"+x+"'", stations))))
            try:
                seat_sqn = max(csr.fetchall())[1]
            except ValueError:
                #assign new seat
                csr.execute('select distinct seat_sqn from seat_booked where train_no = {0} and travel_date = \'{1}\''.format(train_no, travel_date))
                all_seat = set(range(1, 721))
                filled_seat = set(map(lambda x:x[0], csr.fetchall()))
                seat_sqn = min(all_seat - filled_seat)
            
            #booking seat_sqn for all stations travelled
            for stn in stations:
                csr.execute("insert into seat_booked values ({0}, '{1}', {2}, '{3}', '{4}')".format(pnr, stn, seat_sqn, travel_date, train_no))
                self.db.commit()
            return pnr, seat_sqn
            
            
            # csr.execute("insert into ticket (booked_by, psg_name) values ('{0}', '{1}')".format(self.user, psg_name))
        finally:
            self._closeDB()


