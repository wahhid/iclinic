import requests
import json

url = "https://test.owlexa.com/owlexa-api/invoice/v1/sync-transaction"

payload={
    "claimNumber" : "20200200290031",
    "cardNumber": "1000620030002010",
    "paidToProviderAmount": 580000,
    "providerTransactionNumber": "INV-00002"
}
headers = {
  'API-Key': '8HCmYbU+phImFJXgg1hHjpd6HBQFekEUvsn+TGoBDkc=',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

print(response.text)