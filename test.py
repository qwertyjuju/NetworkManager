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

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import sys
import random as rd
import pygame as pg

# paramètres
taille = 300
remplissage = 5
nb_carres= 1
d = 0.1

def lerp(vec1, vec2):
    print(vec2, vec1)
    if vec2[0]-vec1[0] == 0:
        x = vec1[0]
        y = vec2[1]*d
    else:
        if vec2<vec1:
            cd = (vec2[1] + vec1[1]) / (vec2[0] + vec1[0])
            x = (vec2[0] + vec1[0]) * d
            y = cd * x
        else:
            cd = (vec2[1]-vec1[1])/(vec2[0]-vec1[0])
            x = (vec2[0]-vec1[0])*d
            y = cd*x
    print("lerp", x, y)
    return x,y

pg.init()
couleurs = [(0,0,0), (0,128,0), (255, 0, 0), (255, 102, 204), (51, 51, 255), (255, 102, 0), (255, 255, 0),(153, 102, 51)]
border_x = 5
border_y = 5
surface = pg.Surface((taille+(border_x*2), taille+(border_y*2)))
surface.fill((255, 255, 255))
points=[
    (border_x, border_y),
    (taille+border_x, border_y),
    (taille+border_x, taille+border_y),
    (border_x, taille+border_y)
]
couleur = rd.choice(couleurs)
pg.draw.polygon(surface, couleur, points, remplissage)
for i in range(nb_carres):
    saved_p0 = points[0]
    points[0] = lerp(points[0], points[1])
    points[1] = lerp(points[1], points[2])
    points[2] = lerp(points[2], points[3])
    points[3] = lerp(points[3], saved_p0)
    couleur = rd.choice(couleurs)
    pg.draw.polygon(surface, couleur, points, remplissage)
fichier = "suite_carre.png"
pg.image.save(surface, fichier)
print(fichier)