import requests
import json

def get_reservations():
    # Kea Control Agent URL
    url = "http://localhost:8000"

    # Command to get full configuration
    payload = {
        "command": "config-get",
        "service": ["dhcp4"]
    }

    try:
        # Send request to Kea
        response = requests.post(url, json=payload)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Get the configuration arguments
            config = data[0]["arguments"]["Dhcp4"]
            
            # Check for global reservations
            global_reservations = config.get("reservations", [])
            
            # Check for subnet-specific reservations
            subnet_reservations = []
            for subnet in config.get("subnet4", []):
                subnet_id = subnet.get("id")
                for reservation in subnet.get("reservations", []):
                    reservation["subnet-id"] = subnet_id
                    subnet_reservations.append(reservation)
            
            # Print reservations
            print("\nGlobal Reservations:")
            print("-" * 80)
            for res in global_reservations:
                print(f"Hostname: {res.get('hostname', 'N/A')}")
                print(f"IP: {res.get('ip-address', 'N/A')}")
                print(f"MAC: {res.get('hw-address', 'N/A')}")
                print("-" * 80)
            
            print("\nSubnet Reservations:")
            print("-" * 80)
            for res in subnet_reservations:
                print(f"Subnet ID: {res.get('subnet-id', 'N/A')}")
                print(f"Hostname: {res.get('hostname', 'N/A')}")
                print(f"IP: {res.get('ip-address', 'N/A')}")
                print(f"MAC: {res.get('hw-address', 'N/A')}")
                print("-" * 80)

        else:
            print(f"Error: Request failed with status code {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    get_reservations()
