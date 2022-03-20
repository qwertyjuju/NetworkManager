import NetworkCreator as nc

a = nc.Network("192.168.10.0/24", name="lan1")
a.create_subnet()
a.create_json()