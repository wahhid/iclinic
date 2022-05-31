import hashlib
import random
import base64
import urllib
import hmac
 
# data = "yakespentest"
# secretkey = 'Qwerty2022@'
 
data = "testtesttest"
secretkey = '6jCEDC9934'

# Computes the signature by hashing the data with the secret key as the key
signature = hmac.new(secretkey, msg=data, digestmod=hashlib.sha256).digest()
 
# base64 encode...
encodedSignature = base64.encodestring(signature).replace('\n', '')
 
# urlencode...
encodedSignature = urllib.quote(encodedSignature)
 
print("Voila! A signature: " + encodedSignature)