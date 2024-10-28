from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flashing messages

def get_reservations():
    url = "http://localhost:8000"
    payload = {
        "command": "config-get",
        "service": ["dhcp4"]
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            config = data[0]["arguments"]["Dhcp4"]
            
            global_reservations = config.get("reservations", [])
            subnet_reservations = []
            subnets = []
            
            for subnet in config.get("subnet4", []):
                subnet_id = subnet.get("id")
                subnet_network = subnet.get("subnet")
                subnets.append({
                    "id": subnet_id,
                    "network": subnet_network
                })
                for reservation in subnet.get("reservations", []):
                    reservation["subnet-id"] = subnet_id
                    reservation["subnet-network"] = subnet_network
                    subnet_reservations.append(reservation)
            
            return {
                "global_reservations": global_reservations,
                "subnet_reservations": subnet_reservations,
                "subnets": subnets,
                "error": None
            }
        else:
            return {
                "global_reservations": [],
                "subnet_reservations": [],
                "subnets": [],
                "error": f"Error: Request failed with status code {response.status_code}"
            }
    except Exception as e:
        return {
            "global_reservations": [],
            "subnet_reservations": [],
            "subnets": [],
            "error": f"Error: {str(e)}"
        }

def add_reservation(hostname, ip_address, hw_address, subnet_id):
    url = "http://localhost:8000"
    payload = {
        "command": "reservation-add",
        "service": ["dhcp4"],
        "arguments": {
            "reservation": {
                "subnet-id": int(subnet_id),
                "hostname": hostname,
                "ip-address": ip_address,
                "hw-address": hw_address
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data[0].get("result") == 0:
                return True, "Reservation added successfully"
            else:
                return False, f"Error: {data[0].get('text', 'Unknown error')}"
        else:
            return False, f"Error: Request failed with status code {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_reservation(subnet_id, ip_address):
    url = "http://localhost:8000"
    payload = {
        "command": "reservation-del",
        "service": ["dhcp4"],
        "arguments": {
            "subnet-id": int(subnet_id),
            "ip-address": ip_address
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data[0].get("result") == 0:
                return True, "Reservation deleted successfully"
            else:
                return False, f"Error: {data[0].get('text', 'Unknown error')}"
        else:
            return False, f"Error: Request failed with status code {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

@app.route('/')
@app.route('/list')
def list_reservations():
    data = get_reservations()
    print("Global Reservations:", len(data["global_reservations"]))  # Debug print
    print("Subnet Reservations:", len(data["subnet_reservations"]))  # Debug print 
    return render_template('list.html', 
                         global_reservations=data["global_reservations"],
                         subnet_reservations=data["subnet_reservations"],
                         error=data["error"])

@app.route('/add')
def add_reservation_page():
    data = get_reservations()
    return render_template('add.html', 
                         subnets=data["subnets"])

@app.route('/add_reservation', methods=['POST'])
def add_reservation_route():
    hostname = request.form.get('hostname')
    ip_address = request.form.get('ip_address')
    hw_address = request.form.get('hw_address')
    subnet_id = request.form.get('subnet_id')
    
    success, message = add_reservation(hostname, ip_address, hw_address, subnet_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('list_reservations'))

@app.route('/delete_reservation', methods=['POST'])
def delete_reservation_route():
    subnet_id = request.form.get('subnet_id')
    ip_address = request.form.get('ip_address')
    
    success, message = delete_reservation(subnet_id, ip_address)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('list_reservations'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
