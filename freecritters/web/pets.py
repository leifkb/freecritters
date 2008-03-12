# -*- coding: utf-8 -*-

from freecritters.model import \
    Session, Pet, Species, SpeciesAppearance, Appearance, pets, species, \
    appearances, species_appearances
from freecritters.web.application import Response
from freecritters.web.form import Form, TextField, SelectMenu, ColorSelector, \
                                  SubmitButton, RegexValidator, HiddenField
from freecritters.web.modifiers import FormTokenField, \
                                       PetNameNotTakenValidator
import ImageColor
from cStringIO import StringIO
import random
from colorsys import hsv_to_rgb
from itertools import izip
from sqlalchemy import and_
from sqlalchemy.orm import eagerload

DEFAULT_COLOR = (255, 0, 0)

def create_pet(req, species_id):
    req.check_permission(u'create_pet')
    species = Species.query.get(species_id)
    if species is None or not species.creatable:
        return None
    appearance_list = Appearance.query.filter(and_(
        species_appearances.c.species_id==species.c.species_id,
        species_appearances.c.appearance_id==appearances.c.appearance_id,
        appearances.c.creatable==True
    )).order_by(appearances.c.name).all()
    if not appearance_list:
        return None
        
    form = Form(u'post', ('pets.create_pet', dict(species_id=species.species_id)),
        FormTokenField(),
        TextField(u'pet_name', u'Name',
                  modifiers=[RegexValidator(Pet.name_regex,
                                            message=u'Can only contain '
                                                    u'letters, numbers, '
                                                    u'spaces, hyphens, and '
                                                    u'underscores. Can not '
                                                    u'start with a number.'),
                             PetNameNotTakenValidator()]))
                             
    if len(appearance_list) > 1:
        appearance_options = [
            (appearance, appearance.name)
            for appearance in appearance_list
        ]
        form.add_field(SelectMenu(u'appearance', u'Appearance',
                                  options=appearance_options))
        del appearance, appearance_options
    form.add_field(ColorSelector(u'color', u'Color'))
    form.add_field(SubmitButton(title=u'Submit', id_=u'submit'))
    form.add_field(SubmitButton(u'preview', u'Preview'))
        
    defaults = {
        u'color': DEFAULT_COLOR,
        u'appearance': appearance_list[0]
    }
    
    results = form(req, defaults)
    
    appearance = results.get(u'appearance', appearance_list[0]) # Field might not exist
    
    if results.successful and u'preview' not in results:
        pet = Pet(results[u'pet_name'], req.user, species, appearance, results[u'color'])
        Session.save(pet)
        req.redirect('pets.pet_list', created=1)
    else:
        return req.render_template('create_pet_form.mako',
            species=species,
            appearance=appearance,
            color=results[u'color'],
            form=results)
        
def pet_image(req, species_id, appearance_id, color):
    species_appearance = SpeciesAppearance.query.filter_by(
        species_id=species_id, appearance_id=appearance_id
    ).options(
        eagerload('white_picture'),
        eagerload('black_picture')
    ).first()
    if species_appearance is None:
        return None
    last_change = max(species_appearance.last_change,
                      species_appearance.white_picture.last_change,
                      species_appearance.black_picture.last_change)
    req.check_modified(last_change)
    image = species_appearance.pil_image_with_color(color)
    io = StringIO()
    image.save(io, 'PNG')
    return Response(io.getvalue(), mimetype='image/png') \
           .last_modified(last_change)

def pet_list(req):
    req.check_permission(u'create_pet')
    pets = req.user.pets.options(
        eagerload('species_appearance'),
        eagerload('species_appearance.species'),
        eagerload('species_appearance.appearance')
    ).order_by(Pet.unformatted_name).all()
    return req.render_template('pet_list.mako',
        pets=pets
    )

def color_wheel(n):
    starting_point = random.uniform(0.0, 1.0)
    for i in xrange(n):
        r, g, b = hsv_to_rgb((starting_point + 1.0 / n * i) % 1.0, 1.0, 1.0)
        yield int(r * 255), int(g * 255), int(b * 255)
        
def species_list(req):
    req.check_permission(u'create_pet')
    items = []
    lst = list(Species.find_creatable())
    random.shuffle(lst)
    colors = color_wheel(len(lst))
    for species, color in izip(lst, colors):
        appearance = random.choice([sa for sa in species.species_appearances.filter(Appearance.creatable==True)]).appearance
        items.append((species, appearance, color))
    return req.render_template('species_list.mako', items=items)