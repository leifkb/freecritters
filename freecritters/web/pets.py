# -*- coding: utf-8 -*-

from freecritters.model import Pet, Species, SpeciesAppearance, Appearance, \
                               species_appearances, appearances
from freecritters.web.application import FreeCrittersResponse
from freecritters.web.form import Form, TextField, SelectMenu, ColorSelector, \
                                  SubmitButton, RegexValidator, HiddenField
from freecritters.web.modifiers import FormTokenValidator, \
                                       PetNameNotTakenValidator, \
                                       AppearanceModifier
from freecritters.web.links import species_appearance_color_image_link, pet_image_link
import ImageColor
from sqlalchemy import Query, and_, eagerload
from freecritters.web.util import redirect
from colubrid.exceptions import PageNotFound, HttpFound
from cStringIO import StringIO
import random
from colorsys import hsv_to_rgb
from itertools import izip

def create_pet(req, species_id):
    req.check_permission(None)
    species_id = int(species_id)
    species_obj = Query(Species).get(species_id)
    if species_obj is None or not species_obj.creatable:
        raise PageNotFound()
    appearance_list = Query(Appearance).filter(and_(
        species_appearances.c.species_id==species_obj.species_id,
        species_appearances.c.appearance_id==appearances.c.appearance_id,
        appearances.c.creatable==True
    )).order_by(appearances.c.name).list()
    if not appearance_list:
        raise PageNotFound()
    class CreatePetForm(Form):
        method = u'post'
        action = u'/pets/create/%s' % species_id
        fields = [
            HiddenField(u'form_token', modifiers=[FormTokenValidator()]),
            TextField(u'pet_name', u'Name',
                      modifiers=[RegexValidator(Pet.name_regex,
                                                message=u'Can only contain '
                                                        u'letters, numbers, '
                                                        u'spaces, hyphens, and '
                                                        u'underscores. Can not '
                                                        u'start with a number.'),
                                 PetNameNotTakenValidator()])
        ]
        if len(appearance_list) > 1:
            appearance_options = [
                (appearance.appearance_id, appearance.name)
                for appearance in appearance_list
            ]
            fields.append(SelectMenu(u'appearance', u'Appearance',
                                     options=appearance_options,
                                     modifiers=[AppearanceModifier()]))
            del appearance, appearance_options
        fields.append(ColorSelector(u'color', u'Color'))
        fields.append(SubmitButton(title=u'Submit', id_=u'submit'))
        fields.append(SubmitButton(u'preview', u'Preview'))
    defaults = {
        u'form_token': req.form_token(),
        u'color': (255, 0, 0)
    }
    form = CreatePetForm(req, defaults)
    values = form.values_dict()
    if u'appearance' in values:
        appearance = values[u'appearance']
    else:
        appearance = appearance_list[0] # Hooray for arbitrariness!
    if form.was_filled and not form.errors and u'preview' not in values:
        Pet(values[u'pet_name'], req.user, species_obj, appearance, values[u'color'])
        redirect(req, HttpFound, '/pets?created=1')
    else:
        context = {
            'species_name': species_obj.name,
            'species_id': species_obj.species_id,
            'initial_appearance_id': appearance.appearance_id,
            'image': species_appearance_color_image_link(
                species_obj.species_id, appearance.appearance_id, values.get(u'color', (255, 0, 0))
            ),
            'form': form.generate()
        }
        return req.render_template('create_pet_form.html', context)
        
def pet_image(req, species, appearance, color):
    try:
        species = int(species)
        appearance = int(appearance)
        color = ImageColor.getrgb('#' + color)
    except ValueError:
        raise PageNotFound()
    species_appearance = Query(SpeciesAppearance).get_by(
        species_id=species, appearance_id=appearance
    )
    if species_appearance is None:
        raise PageNotFound()
    image = species_appearance.pil_image_with_color(color)
    io = StringIO()
    image.save(io, 'PNG')
    return FreeCrittersResponse(
        io.getvalue(),
        [('Content-Type', 'image/png')]
    )
    
def pet_list(req):
    req.check_permission(None)
    pets = []
    for pet in Query(Pet).filter(Pet.c.user_id==req.user.user_id).order_by(Pet.c.name):
        pets.append({
            'image': pet_image_link(pet),
            'name': pet.name,
            'appearance': pet.appearance.name,
            'species': pet.species.name,
            'color': pet.color,
        })
    return req.render_template('pet_list.html',
        pets=pets,
        created='created' in req.args
    )

def color_wheel(n):
    starting_point = random.uniform(0.0, 1.0)
    for i in xrange(n):
        r, g, b = hsv_to_rgb((starting_point + 1.0 / n * i) % 1.0, 1.0, 1.0)
        yield int(r * 255), int(g * 255), int(b * 255)
        
def species_list(req):
    req.check_permission(None)
    species_ctx = []
    lst = Query(Species).options(eagerload('appearances')).list()
    lst = [item for item in lst if item.can_be_created]
    random.shuffle(lst)
    colors = list(color_wheel(len(lst)))
    for species, color in izip(lst, colors):
        appearance = random.choice([x.appearance for x in species.appearances if x.appearance.creatable])
        species_ctx.append({
            'name': species.name,
            'link': u'/pets/create/%s' % species.species_id,
            'image': species_appearance_color_image_link(species, appearance, color)
        })
    return req.render_template('species_list.html', species=species_ctx)