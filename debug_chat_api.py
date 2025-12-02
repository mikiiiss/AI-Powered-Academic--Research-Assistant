import requests
import json

url = 'http://localhost:5000/api/chat'
headers = {'Content-Type': 'application/json'}
data = {'query': 'Find recent papers on dark matter and identify research gaps'}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        json_response = response.json()
        print("\nFull JSON Response:")
        print(json.dumps(json_response, indent=2))
        
        # Check specific fields
        print("\n--- Analysis ---")
        if 'tool_results' in json_response:
            print(f"tool_results found: {len(json_response['tool_results'])} items")
            for item in json_response['tool_results']:
                print(f" - Tool: {item.get('tool_name')}")
                result = item.get('result')
                if isinstance(result, list):
                    print(f"   Result count: {len(result)}")
                else:
                    print(f"   Result type: {type(result)}")
        else:
            print("❌ 'tool_results' missing from response")
            
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Exception: {e}")
