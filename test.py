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

from DeviceLoader import ConfigParser

a = ConfigParser("data/configs/test.json")

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