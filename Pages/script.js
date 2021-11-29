// import hash from 'essentials.js'
hashCode = function(s){
    return s.split("").reduce(function(a,b){a=((a<<5)-a)+b.charCodeAt(0);return a&a},0);              
};
sendReq = function(endpoint, params){
    url = 'http://127.0.0.1:5000/'+endpoint+'/'+params
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.responseType = 'json';
    xhr.onload = () => {
        const data = xhr.response;
    }
    xhr.send()
    return data, xhr.status;
};
login = function(){
    user = document.getElementById('for_username').value
    password = document.getElementById('for_password').value
    url = 'http://127.0.0.1:5000/login/' + user + '/'+hashCode(password)
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.responseType = 'json';
    xhr.onload = () => {
        const data = xhr.response;
        console.log(data);
        if (xhr.status == 200){
            alert('Log In successful')
        }
        else if(xhr.status == 401){
            alert('Username or password is incorrect')
        }
        else{
            alert('some error occoured')
        }
    };
    xhr.send()
};
pnr_status = function(){
    pnr = document.getElementById('pnr1').value
    url = 'http://127.0.0.1:5000/pnr/'+pnr
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.responseType = 'json';
    xhr.onload = () => {
        const data = xhr.response;
        console.log(data);
        document.getElementById('for_booked_by').value = data['booked_by']
        document.getElementById('for_passgn-name').value = data['psg_name']
        document.getElementById('for_travel-date').value = data['travel_date']
        document.getElementById('for_train-no').value = data['train_no']
        document.getElementById('for_first-statn').value = data['first_stn']
        document.getElementById('for_last-statn').value = data['last_stn']
        document.getElementById('for_coach').value = data['coach']
        document.getElementById('for_seat').value = data['seat']
    }
    xhr.send()
};


seat_availability = function(){
    date = document.getElementById('for_date-for-travel').value
    train_no = document.getElementById('for_train-no').value
    frm = document.getElementById('for_stations_from').value
    to = document.getElementById('for_stations_to').value
    url = 'http://127.0.0.1:5000/seat-availibility/'+frm+'/'+to+'/'+train_no+'/'+date
    const xhr = new XMLHttpRequest()
    // value = {'stn_frm': frm, 'stn_to': to, 'travel_date': date, 'train_no': train_no}
    // console.log(value)
    xhr.open('GET', url)
    xhr.responseType = 'json'
    xhr.onload = () =>{
        const data = xhr.response;
        document.getElementById('for_available-seat').value = data['avail']
    }
    xhr.send()
    
}

signup = function(){
    if(document.getElementById('for_password').value != document.getElementById('for_confirm-password').value){
        console.log(document.getElementById('for_password').value)
        console.log(document.getElementById('for_confirm-password').value)
        alert('password does not match')
        return;
    }
    user = document.getElementById('for_username').value
    psw = hashCode(document.getElementById('for_password').value+"")
    nme = document.getElementById('for_name').value
    date = document.getElementById('for_dob').value
    mob = document.getElementById('for_mobile').value
    email = document.getElementById('for_email').value
    address = document.getElementById('for_address').value
    url = 'http://127.0.0.1:5000/signup/'+user+'/'+psw+'/'+nme+'/'+date+'/'+mob
    console.log(url)
    if(email != ''){
        url = url + '/'+email
    }
    if(address != ''){
        url = url + '/' + address
    }
    console.log(url)
    const xhr = new XMLHttpRequest()
    xhr.open('GET', url)
    xhr.response = 'json'
    xhr.onload = ()=>{
        const data = xhr.response
        if (xhr.status == 201){
            alert('success')
        }
        else{
            alert('error')
        }
    }
    xhr.send()
    
}
routechecking = function(){
    // par.preventDefault
    t_no = document.getElementById('for_train-no').value;
    console.log(t_no)
    url = 'http://127.0.0.1:5000/route/'+t_no
    const xhr = new XMLHttpRequest()
    xhr.open("GET", url)
    xhr.response = 'json'
    xhr.onload =()=>{
        const data = JSON.parse(xhr.response)
        console.log(data)
        document.getElementById('for_psg-name').value = data["name"]
        document.getElementById('for_coach').value = data['total_coach']
        document.getElementById('for_running-days').value = data['running_days']
        table = document.getElementById('table-body')
        for(let i = 0; i<data['time_table'].length; i++){
            row = table.insertRow(i)
            for(let j =0; j<data['time_table'][i].length; j++){
                row.insertCell(j).innerHTML = data['time_table'][i][j]
            }
        }
    }

    xhr.send()
};
train_betn_stations = function(){
    frm = document.getElementById('for_stations_from').value
    to = document.getElementById('for_stations_to').value
    url = 'http://127.0.0.1:5000/train-bw-stations/'+frm+'/'+to
    const xhr = new XMLHttpRequest()
    xhr.open("GET", url)
    xhr.response = 'json'
    table = document.getElementById('table-body')
    xhr.onload = () =>{
        const data = JSON.parse(xhr.response)
        console.log(data)
        for(let i = 0; i<data.length; i++){
            row = table.insertRow(i)
            row.insertCell(0).innerHTML = data[i]['train_no']
            row.insertCell(1).innerHTML = data[i]['name']
            row.insertCell(2).innerHTML = data[i]['departure']
            row.insertCell(3).innerHTML = data[i]['day_no_frm']
            row.insertCell(4).innerHTML = data[i]['arrival']
            row.insertCell(5).innerHTML = data[i]['day_no_to']
        }
    }
    xhr.send()
}