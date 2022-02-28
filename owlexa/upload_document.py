#from requests import Request, Session
import requests

url = "https://test.owlexa.com/owlexa-api/invoice/v1/upload-document"

multipart_form_data = {
    'file': ('account.invoice-58-invoice_pdf_file.pdf',open('/Users/whidayat/Downloads/account.invoice-58-invoice_pdf_file.pdf','rb'),'application/pdf'),
    'includeInvoice': (None, 'true'),
    'providerTransactionNumber': (None, 'INV-00001')
}

payload={
    "providerTransactionNumber": "INV-00001",
    "includeInvoice": "true"
}

files=[
  ('file',('account.invoice-58-invoice_pdf_file.pdf',open('/Users/whidayat/Downloads/account.invoice-58-invoice_pdf_file.pdf','rb'),'application/pdf'))
]

headers = {
  #'Content-Type': 'multipart/form-data',
  'API-Key': '8HCmYbU+phImFJXgg1hHjpd6HBQFekEUvsn+TGoBDkc='
}

#request = Request('POST', url, headers=headers, data=payload, files=files).prepare()
#print(request.body)
#s = Session()
#response = s.send(request)
#print(response.request.url)
#print(response.request.body)
#print(response.request.headers)
response = requests.post( url, headers=headers, data=payload, files=files)
print(response.text)