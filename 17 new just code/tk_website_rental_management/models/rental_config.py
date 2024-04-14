# -*- coding: utf-8 -*-
# Copyright (C) 2023-TODAY TechKhedut (<https://www.techkhedut.com>)
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class PropertyRentalConfig(models.Model):
    """Theme Config"""
    _name = 'property.theme.config'
    _description = __doc__

    name = fields.Char(string="Title", default="Property Website Home Configuration")
    no_latest_list = fields.Integer(string="No. of Latest Listing", default=10, required=True)
    no_popular_list = fields.Integer(string="No. of Popular Listing", default=10, required=True)
    google_map_api = fields.Char(string="Google Map API Key")
    map_center_address = fields.Char(string="Map Center Address", default="USA")
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    zoom_level = fields.Integer(string="Zoom Level", default="6")
    review_ids = fields.Many2many('property.website.reviews', string="Website Reviews")
    video_link = fields.Char(string="Video Link")
    partner_ids = fields.Many2many('property.website.partner', string="Partners")
    city_ids = fields.One2many('property.by.city', 'config_id', string="Cities")
    mailling_list_id = fields.Many2one('mailing.list', string="Newsletter")
    list_property_per_page = fields.Integer(string='Listing Properties per Page', default=12, required=True)

    hs_one = fields.Integer(string="Home stats 1", default=1254)
    hs_two = fields.Integer(string="Home stats 2", default=12168)
    hs_three = fields.Integer(string="Home stats 3", default=2172)
    hs_four = fields.Integer(string="Home stats 4", default=732)

    # price filters
    price_start = fields.Integer(string="Price Start Range", default=0)
    price_end = fields.Integer(string="Price End Range", default=50000)
    # area filters
    area_start = fields.Integer(string="Area Start Range", default=0)
    area_end = fields.Integer(string="Area End Range", default=5000)
    # show landlord
    display_landlord = fields.Boolean(string="Display Landlord on Property ?", default=True)
    # Section Search Images
    hero_choice = fields.Selection([('img', "Image Background"), ('vid', "Video Background"),
                                    ('youtube', "Youtube Video")], default='img',
                                   string="Search Section Background Type")
    video_bg_url = fields.Char(string="Video URL")
    youtube_bg_video = fields.Char(string="Youtube Video ID")
    mob_background = fields.Binary(string="Mobile BG Image for video")
    image_1920_0 = fields.Binary(string="Main BG Image")
    image_1920_1 = fields.Binary(string="Any Status BG Image")
    image_1920_2 = fields.Binary(string="For Sale BG Image")
    image_1920_3 = fields.Binary(string="For Rent BG Image")
    # Section 2 & # BG Images
    sec_img_2 = fields.Binary(string="Stats BG Image")
    sec_img_3 = fields.Binary(string="Promo Video BG Image")

    is_rtl = fields.Boolean(string="Is RTL Enable ?")


class PropertyWebsiteReview(models.Model):
    """Property Rental Website Reviews"""
    _name = 'property.website.reviews'
    _description = __doc__

    name = fields.Char(string="Name", required=True)
    image_1920 = fields.Binary(string="Profile Image")
    role = fields.Char(string="Role", required=True)
    rate = fields.Selection([('1', '1 Star'), ('2', '2 Stars'), ('3', "3 Stars"), ('4', '4 Stars'), ('5', '5 Stars')],
                            string="Rating", default='5', required=True)
    reviews = fields.Text(string="Reviews")


class PropertyWebsitePartners(models.Model):
    """Property Website Partners"""
    _name = 'property.website.partner'
    _description = __doc__

    name = fields.Char(string="Name", required=True)
    partner_logo = fields.Binary(string="Image", required=True)


class PropertiesByCity(models.Model):
    """Properties by city"""
    _name = 'property.by.city'
    _rec_name = 'city_id'
    _description = __doc__

    sequence = fields.Integer()
    property_count = fields.Integer(compute='_compute_property_total_counts', string="No. of Properties")
    city_id = fields.Many2one('property.res.city', required=True, string="City")
    cover_image = fields.Binary(string="Image", required=True)
    size = fields.Selection([('4', "4"), ('6', "6"), ('8', "8"), ('10', "10"), ('12', "12")], default='4',
                            required=True)
    tag_line = fields.Text(string="Tag Line", default="Constant care and attention to the patients makes good record")
    config_id = fields.Many2one('property.theme.config')

    @api.depends('city_id')
    def _compute_property_total_counts(self):
        """Total number of properties by city"""
        for rec in self:
            count = 0
            if rec.city_id:
                count = self.env['property.details'].sudo().search_count(
                    [('stage', '=', 'available'), ('city_id', '=', rec.city_id.id)])
            rec.property_count = count
