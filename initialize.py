import mysql.connector

try:
    #connects to database using the details
    db = mysql.connector.connect(
        host = 'localhost',
        user = 'rail_api',
        password = 'railpassword',
        database = 'railway_management_system'
    )
    csr = db.cursor(buffered = True)

    try:
        csr.execute(
        '''Create table User(
            username varchar(10) primary key,
            password varchar(40) not null,
            name varchar(40) not null,
            dob date not null,
            mobile char(10) not null,
            email varchar(60),
            address varchar(100)
        );''')
    except Exception:
        #this gets executed if the table alreadt exists
        pass
    try:
        csr.execute(
        '''create table stations(
            code char(4) primary key,
            name varchar(40) not null
        );''')
    except Exception:
        #this gets executed if the table alreadt exists
        pass
    try:
        csr.execute(
        '''create table trains(
            train_no char(5) primary key,
            name varchar(40),
            total_coach tinyint not null,
            days varchar(7) not null
        );''')
    except Exception:
        #this gets executed if the table alreadt exists
        pass
    try:
        csr.execute(
        '''create table ticket(
            pnr char(8) primary key,
            booked_by varchar(10) not null,
            psg_name varchar(40) not null,
            foreign key(booked_by) references User(username) on update restrict
        );''')
    except Exception:
        #this gets executed if the table alreadt exists
        pass
    try:
        csr.execute(
        '''create table seat_booked(
            pnr char(8) references ticket(pnr) on update restrict,
            stn_code char(4) references stations(code) on update restrict,
            seat_sqn tinyint not null,
            travel_date date not null,
            train_no char(5) references trains(train_no) on update restrict,
            primary key(pnr, stn_code, seat_sqn, travel_date, train_no)
        );''')
    except Exception:
        #this gets executed if the table alreadt exists
        pass
    try:
        csr.execute(
        '''create table time_table(
            stn_code char(4) references stations(code) on update restrict,
            train_no char(5) references trains(train_no) on update restrict,
            arrival time,
            departure time,
            day_no tinyint,
            platform_no tinyint
        );''')
    except Exception:
        #this gets executed if the table alreadt exists
        pass

    #commits the created tables to storage
    db.commit()

finally:
    #closed the database connection
    db.close()
