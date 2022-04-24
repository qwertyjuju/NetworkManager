"""
import re

commands = {
    "ports configuration":{
        "%{forloop(%ports%)}":[
            "int %()"
        ],
    }
}

se = re.compile("%\((\w+)\(\((w+)\)\)")
text="int %(forloop(test)) ceci est un test %(testvar(test))"
print(re.findall(se, text))
"""
"""
from DeviceLoader import ConfigParser

a = ConfigParser("data/configs/test.json")
"""
"""
import re
test = ["0,1,3,4-5", "a,b,d-e", "8-,7_,7", "0-3"]
res = re.compile("^[0-9]+[^a-zA-Z]")
for text in test:
    resultat =re.search(res, text)
    if resultat:
        print(resultat.groups())
    print(re.findall(res,text))
    print("############################")
"""

# Using @property decorator
class Celsius:
    def __init__(self, temperature=0):
        self.temperature = temperature

    def to_fahrenheit(self):
        return (self.temperature * 1.8) + 32

    @property
    def temperature(self):
        print("Getting value...")
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        print("Setting value...")
        if value < -273.15:
            raise ValueError("Temperature below -273 is not possible")
        self._temperature = value


# create an object
human = Celsius(37)

print(human.temperature)

print(human.to_fahrenheit())

coldest_thing = Celsius(-300)