import bcrypt

password = b"zakaznik"  # Sem napiš nové heslo
hash = bcrypt.hashpw(password, bcrypt.gensalt())
print(hash.decode())
