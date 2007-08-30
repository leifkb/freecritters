# -*- coding: utf-8 -*-

def user_link(user):
    return u'/users/%s' % user.unformatted_username.encode('ascii')
    
def conversation_link(conversation):
    try:
        conversation = conversation.conversation_id
    except AttributeError:
        pass
    return u'/mail/%s' % conversation

def species_appearance_color_image_link(species, appearance, color):
    try:
        species = species.species_id
    except AttributeError:
        pass
    try:
        appearance = appearance.appearance_id
    except AttributeError:
        pass
    return u'/pets/images/%s/%s/%02X%02X%02X.png' % ((species, appearance) + color)
    
def pet_image_link(pet):
    return species_appearance_color_image_link(pet.species, pet.appearance, pet.color)