# -*- coding: utf-8 -*-

from freecritters.model import Pet, Species, SpeciesAppearance, Appearance
from freecritters.web.application import FreeCrittersResponse
from freecritters.web.form import Form, TextField, SelectMenu, ColorSelector, \
                                  SubmitButton, RegexValidator, HiddenField
from freecritters.web.modifiers import FormTokenValidator, \
                                       PetNameNotTakenValidator, \
                                       AppearanceModifier
from freecritters.web.links import species_appearance_color_image_link, pet_image_link
import ImageColor
from freecritters.web.util import redirect
from colubrid.exceptions import PageNotFound, HttpFound
from cStringIO import StringIO
import random
from colorsys import hsv_to_rgb
from itertools import izip

def create_pet(req, species_id):
    req.check_permission(None)
    species = Species.get(int(species_id))
    if species is None or not species.creatable:
        raise PageNotFound()
    appearances = list(species.appearances.find(creatable=True) \
                      .order_by(Appearance.name))
    if not appearances:
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
        if len(appearances) > 1:
            appearance_options = [
                (appearance.appearance_id, appearance.name)
                for appearance in appearances
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
        appearance = appearances[0] # Hooray for arbitrariness!
        
    if form.was_filled and not form.errors and u'preview' not in values:
        Pet(values[u'pet_name'], req.user, species, appearance, values[u'color']).save()
        redirect(req, HttpFound, '/pets?created=1')
    else:
        context = {
            'species_name': species.name,
            'species_id': species.species_id,
            'initial_appearance_id': appearance.appearance_id,
            'image': species_appearance_color_image_link(
                species.species_id, appearance.appearance_id, values.get(u'color', (255, 0, 0))
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
    species_appearance = SpeciesAppearance.find(
        species_id=species, appearance_id=appearance
    ).one()
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
    for pet in req.user.pets.order_by(Pet.name):
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
    lst = list(Species.find_creatable())
    random.shuffle(lst)
    colors = list(color_wheel(len(lst)))
    for species, color in izip(lst, colors):
        appearance = random.choice([appearance for appearance in species.appearances if appearance.creatable])
        species_ctx.append({
            'name': species.name,
            'link': u'/pets/create/%s' % species.species_id,
            'image': species_appearance_color_image_link(species, appearance, color)
        })
    return req.render_template('species_list.html', species=species_ctx)