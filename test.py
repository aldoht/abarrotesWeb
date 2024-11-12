import hashlib

print(hashlib.pbkdf2_hmac('sha256', 'contra'.encode('utf-8'), b'', 100000).hex())