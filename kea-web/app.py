from flask import Flask, render_template
import requests

app = Flask(__name__)

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
            
            for subnet in config.get("subnet4", []):
                subnet_id = subnet.get("id")
                subnet_network = subnet.get("subnet")
                for reservation in subnet.get("reservations", []):
                    reservation["subnet-id"] = subnet_id
                    reservation["subnet-network"] = subnet_network
                    subnet_reservations.append(reservation)
            
            return {
                "global_reservations": global_reservations,
                "subnet_reservations": subnet_reservations,
                "error": None
            }
        else:
            return {
                "global_reservations": [],
                "subnet_reservations": [],
                "error": f"Error: Request failed with status code {response.status_code}"
            }
    except Exception as e:
        return {
            "global_reservations": [],
            "subnet_reservations": [],
            "error": f"Error: {str(e)}"
        }

@app.route('/')
def home():
    data = get_reservations()
    return render_template('index.html', 
                         global_reservations=data["global_reservations"],
                         subnet_reservations=data["subnet_reservations"],
                         error=data["error"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
