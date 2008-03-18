# -*- coding: utf-8 -*-

from freecritters.model import User
from random import choice

def profile(req, username):
    user = User.find_user(username)
    if user is None:
        return None
    
    pets = user.pets.all()
    if pets:
        pet = choice(pets)
    else:
        pet = None
    
    return req.render_template('profile.mako',
        user=user,
        groups=user.group_list,
        pets=pets,
        pet=pet,
        pet_count=len(pets))