# -*- coding: utf-8 -*-
# Copyright (C) 2023-TODAY TechKhedut (<https://www.techkhedut.com>)
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import http, _
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.image import image_data_uri
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


def category_wise_domain_filter(list_type):
    """Category wise domain filter for property"""
    list_domain = []
    if list_type and list_type == 'lands':
        list_domain.append(('type', '=', 'land'))
    if list_type and list_type == 'residential':
        list_domain.append(('type', '=', 'residential'))
    if list_type and list_type == 'commercial':
        list_domain.append(('type', '=', 'commercial'))
    if list_type and list_type == 'industrial':
        list_domain.append(('type', '=', 'industrial'))
    return list_domain


# DYNAMIC CATEGORY FILTER
def dynamic_category_filter(vals):
    """Dynamic Amenities"""
    dc_catg = None
    if vals.get('dc'):
        dc_catg = vals.get('dc')
    return dc_catg


def convert_str_to_dict(input_string):
    # Split the string into key-value pairs
    pairs = input_string.split("&")

    # Create a dictionary to store the key-value pairs
    result_dict = {}

    # Iterate over each pair and add it to the dictionary
    for pair in pairs:
        # Split the pair into key and value
        key, value = pair.split("=")

        # Add key-value pair to the dictionary
        result_dict[key] = value

    # Display the resulting dictionary
    return result_dict


def get_amenities_filters(param):
    """Amenities wise domain filter of property"""
    url_args, list_domain = dict(), []
    # Amenities filter - gym
    args = None
    if param.get('facility'):
        args = param.get('facility').split(',')
    if args and 'gym' in args:
        url_args['facility'] = 'gym'
        list_domain.append(('web_gym', '=', True))
    # wifi
    if args and 'wifi' in args:
        url_args['facility'] = 'wifi'
        list_domain.append(('web_wifi', '=', True))
    # parking
    if args and 'parking' in args:
        url_args['facility'] = 'parking'
        list_domain.append(('web_parking', '=', True))
    # pool
    if args and 'pool' in args:
        url_args['facility'] = 'pool'
        list_domain.append(('web_pool', '=', True))
    # security
    if args and 'security' in args:
        url_args['facility'] = 'security'
        list_domain.append(('web_security', '=', True))
    # laundry
    if args and 'laundry' in args:
        url_args['facility'] = 'laundry'
        list_domain.append(('web_laundry', '=', True))
    # Equipped Kitchen
    if args and 'kitchen' in args:
        url_args['facility'] = 'kitchen'
        list_domain.append(('web_equip_kitchen', '=', True))
    # AC
    if args and 'air' in args:
        url_args['facility'] = 'air'
        list_domain.append(('web_air_condition', '=', True))
    # semi furnish
    if args and 'sfur' in args:
        url_args['facility'] = 'sfur'
        list_domain.append(('web_semi_furnish', '=', True))
    # full furnish
    if args and 'fuf' in args:
        url_args['facility'] = 'fuf'
        list_domain.append(('web_full_furnish', '=', True))
    # Alarm
    if args and 'alarm' in args:
        url_args['facility'] = 'alarm'
        list_domain.append(('web_alarm', '=', True))
    # window cover
    if args and 'window' in args:
        url_args['facility'] = 'window'
        list_domain.append(('web_window_cover', '=', True))

    return url_args, list_domain


def property_filters(param):
    """Get all filters together"""
    url_args, list_domain = dict(), []
    # status filters
    status = param.get('st')
    if status and status in ['sale', 'rent']:
        url_args['st'] = status
        if status == 'sale':
            list_domain.append(('sale_lease', '=', 'for_sale'))
        else:
            list_domain.append(('sale_lease', '=', 'for_tenancy'))

        # price range filters - starting price
        price_start = param.get('price-start')
        if price_start and price_start.isdigit():
            if status == 'sale':
                url_args['price-start'] = price_start
                list_domain.append(('price', '>=', int(price_start)))
            else:
                list_domain.append(('price', '>=', int(price_start)))
        # price range filters - ending price
        price_end = param.get('price-end')
        if price_end and price_end.isdigit():
            url_args['price-end'] = price_end
            if status == 'sale':
                list_domain.append(('price', '<=', int(price_end)))
            else:
                list_domain.append(('price', '<=', int(price_end)))

    # city filters
    city = param.get('cn')
    if city and 'All' not in city:
        cities = request.env['property.res.city'].sudo().search([('name', '=', str(city))]).ids
        if cities:
            url_args['cn'] = city
            list_domain.append(('city_id', 'in', cities))

    # Dynamic Category Filters
    dc_categ = param.get('dc')
    if dc_categ and dc_categ.isdigit():
        url_args['dc'] = dc_categ
        list_domain.append(('property_subtype_id', '=', int(dc_categ)))

    # category filters
    categ = param.get('categ')
    if categ and len(categ) > 0 and 'All' not in categ:
        url_args['categ'] = categ
        list_domain = list_domain + category_wise_domain_filter(categ)

        # area filters
        area_start = param.get('area-start')
        area_end = param.get('area-end')
        if area_start and area_start.isdigit() and area_end and area_end.isdigit():
            url_args['area-start'] = area_start
            url_args['area-end'] = area_end
            if categ in ('residential', 'commercial', 'industrials', 'lands'):
                list_domain.append(('total_area', '>=', int(area_start)))
                list_domain.append(('total_area', '<=', int(area_end)))

    # max price filters
    max_price = param.get('max_prc')
    if max_price and max_price.isdigit():
        url_args['max_prc'] = max_price
        if status and status in ['sale', 'rent']:
            list_domain.append(('price', '<=', int(max_price)))
            if status == 'sale':
                list_domain.append(('sale_lease', '=', 'for_sale'))
            else:
                list_domain.append(('sale_lease', '=', 'for_tenancy'))
        else:
            list_domain.append(('price', '<=', int(max_price)))

    # search term filters
    search_term = param.get('search_term')
    if search_term:
        url_args['search_term'] = search_term
        list_domain.append(('name', 'ilike', search_term))

    # bedrooms filters
    bedrooms = param.get('rooms')
    if bedrooms and bedrooms.isdigit():
        url_args['rooms'] = bedrooms
        if int(bedrooms) >= 10:
            list_domain.append(('bed', '>=', bedrooms))
        else:
            list_domain.append(('bed', '=', bedrooms))

    # bathrooms filters
    bathrooms = param.get('bathrooms')
    if bathrooms and bathrooms.isdigit():
        url_args['bathrooms'] = bathrooms
        if int(bathrooms) >= 10:
            list_domain.append(('bathroom', '>=', bathrooms))
        else:
            list_domain.append(('bathroom', '=', bathrooms))

    # floor filters
    floor = param.get('floor')
    if floor and floor.isdigit():
        url_args['floor'] = floor
        if int(floor) >= 10:
            list_domain.append(('total_floor', '>=', floor))
        else:
            list_domain.append(('total_floor', '=', floor))

    return url_args, list_domain


def property_sorting_orders(param):
    """Sorting order of property records"""
    url_args, default_order = dict(), ""
    # Property type sort filter
    property_type = param.get('property_type')
    if property_type and property_type in ['sale', 'rent']:
        url_args['property_type'] = property_type
        if property_type == 'sale':
            default_order = 'sale_lease ASC'
        else:
            default_order = 'sale_lease DESC'
    else:
        default_order = 'id DESC'
    # Price order sort filter
    price_order = param.get('price_order')
    if price_order and property_type and property_type in ('sale', 'rent') and price_order in ('lh', 'hl'):
        url_args['price_order'] = price_order
        if price_order == 'lh':
            default_order += ',' + 'tenancy_price ASC' if property_type == 'rent' else ',' + 'sale_price ASC'
        else:
            default_order += ',' + 'tenancy_price DESC' if property_type == 'rent' else ',' + 'sale_price DESC'
    return url_args, default_order


def get_all_filters(param):
    """Combine filters & Sorting orders"""
    # query param args
    url_args, list_domain = dict(), []

    # sorting orders
    sort_args, default_order = property_sorting_orders(param)
    url_args.update(sort_args)

    # property filters
    filter_args, prop_list_domain = property_filters(param)
    url_args.update(filter_args)
    list_domain = list_domain + prop_list_domain

    # amenities filters
    ame_args, ame_filters = get_amenities_filters(param)
    url_args.update(ame_args)
    list_domain = list_domain + ame_filters

    return url_args, list_domain, default_order


def dynamic_amenities_list(vals):
    """Dynamic Amenities"""
    da_list = None
    if vals.get('da'):
        da_str = vals.get('da')[:-1]
        if len(da_str) > 0:
            da_str_lst = da_str.split(',')
            da_list = [int(i) for i in da_str_lst]
    return da_list


class PropertyController(Website):
    """Property website"""

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        """Home page of property management"""
        # theme config rec
        home_config = request.env.ref('tk_website_rental_management.property_theme_config_rec')
        # property details env
        property_param = request.env['property.details'].sudo()
        # latest listing
        latest_listing = property_param.search(
            [('stage', '=', 'available'), ('company_id', 'in', [request.website.company_id.id, False])],
            order='id desc',
            limit=home_config.no_latest_list)
        # popular listing
        popular_listing = property_param.search([('stage', '=', 'available'), ('is_popular_list', '=', True),
                                                 ('company_id', 'in', [request.website.company_id.id, False]), ],
                                                order='id desc', limit=home_config.no_popular_list)

        # Hero Categories
        hero_categories = request.env['property.sub.type'].sudo().search([('display_on_home', '=', True)], limit=8,
                                                                         order='sequence asc')

        book_prop = request.env['property.bookmark'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)]).mapped('property_id').ids
        ctx = {
            'latest_listing': latest_listing,
            'popular_listing': popular_listing,
            'hero_categories': hero_categories,
            'home_config': home_config,
            'book_properties': book_prop,
            'book_property_count': len(book_prop),
            'cities': property_param.get_all_cities(),
        }
        return request.render("tk_website_rental_management.homes", ctx)

    def get_dynamic_amenity_filter(self, da_list):
        # Get leads values
        query = """
            SELECT
            property_id
            FROM
            property_website_amenity_rel
            WHERE amenity_id IN %s
        """
        request._cr.execute(query, [tuple(da_list)])
        properties = [i[0] for i in request._cr.fetchall()]
        return [('id', 'in', properties)]

    @http.route(['/properties-list',
                 '/properties-list/page/<int:page>',
                 '/properties-list/<string:list_type>',
                 '/properties-list/<string:list_type>/page/<int:page>'], type='http', auth="public", website=True)
    def properties_list(self, list_type=None, page=0, **kw):
        """List of properties"""
        property_param = request.env['property.details'].sudo()
        # theme config rec
        config_rec = request.env.ref('tk_website_rental_management.property_theme_config_rec')
        # domain list
        list_domain = [('stage', '=', 'available')]
        # category wise filter domain
        if list_type:
            list_domain = list_domain + category_wise_domain_filter(list_type)

        # Property filters
        url_args, prop_filters, default_order = get_all_filters(request.params)
        list_domain = list_domain + prop_filters
        # multi company
        list_domain = list_domain + [('company_id', 'in', [request.website.company_id.id, False])]
        # Dynamic Amenities
        da_list = dynamic_amenities_list(request.params)
        if da_list:
            properties = self.get_dynamic_amenity_filter(da_list)
            list_domain = list_domain + properties

        # property list limit
        property_per_page = config_rec.list_property_per_page
        list_count = property_param.search_count(list_domain)

        # pagination
        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=list_count,
            page=page,
            step=property_per_page,
            url_args=url_args,
        )
        # listings
        listing = property_param.search(list_domain, order=default_order, offset=pager['offset'],
                                        limit=property_per_page)

        book_prop = request.env['property.bookmark'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)]).mapped('property_id').ids

        dynamic_amenity_ids = request.env['property.amenities'].sudo().search([('is_on_website', '=', True)])

        # Categories
        category_domain = []
        if kw.get('categ'):
            category_domain = category_domain + [('type', '=', kw.get('categ'))]
        categories = request.env['property.sub.type'].sudo().search(category_domain, order='sequence asc')
        ctx = {
            'listing': listing,
            'list_type': list_type,
            'pager': pager,
            'cities': property_param.get_all_cities(),
            'theme_config': config_rec,
            'book_properties': book_prop,
            'book_property_count': len(book_prop),
            'da_ids': dynamic_amenity_ids,
            'da_list': da_list,
            'categories': categories,
        }
        return request.render("tk_website_rental_management.property_list", ctx)

    @http.route(['/properties/city/<model("property.res.city"):city>/',
                 '/properties/city/<model("property.res.city"):city>/page/<int:page>'], type='http', auth="public",
                website=True)
    def properties_list_by_city(self, city, page=0):
        """City wise property list"""
        # theme config rec
        config_rec = request.env.ref('tk_website_rental_management.property_theme_config_rec')
        property_param = request.env['property.details'].sudo()
        # domain list city wise
        list_domain = [('stage', '=', 'available'), ('city_id', '=', city.id)]

        # Property filters
        url_args, prop_filters, default_order = get_all_filters(request.params)
        list_domain = list_domain + prop_filters
        # multi company
        list_domain = list_domain + [('company_id', 'in', [request.website.company_id.id, False])]
        # limit per page
        property_per_page = config_rec.list_property_per_page
        list_count = property_param.search_count(list_domain)

        # Dynamic Amenities
        da_list = dynamic_amenities_list(request.params)
        if da_list:
            properties = self.get_dynamic_amenity_filter(da_list)
            list_domain = list_domain + properties

        # Pagination
        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=list_count,
            page=page,
            step=property_per_page,
            url_args=url_args,
        )
        listing = property_param.search(list_domain, order=default_order, offset=pager['offset'],
                                        limit=property_per_page)

        book_prop = request.env['property.bookmark'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)]).mapped('property_id').ids
        dynamic_amenity_ids = request.env['property.amenities'].sudo().search([('is_on_website', '=', True)])
        ctx = {
            'listing': listing,
            'pager': pager,
            'city': city,
            'cities': property_param.get_all_cities(),
            'theme_config': config_rec,
            'book_properties': book_prop,
            'book_property_count': len(book_prop),
            'da_ids': dynamic_amenity_ids,
            'da_list': da_list,
        }
        return request.render("tk_website_rental_management.property_list", ctx)

    @http.route('/property-details/<model("property.details"):prop>', type='http', auth="public", website=True)
    def property_details(self, prop, **kw):
        """Get single property details"""
        error_msg, enquiry_made = False, False
        if request.httprequest.method == 'POST':
            # Enquiry form validation
            if not kw.get('name'):
                error_msg = 'Name is required'
            if not kw.get('email'):
                error_msg = 'Email is required'
            if not kw.get('mobile'):
                error_msg = 'Mobile is required'
            # Create lead
            if not error_msg:
                lead_data = {
                    'name': prop.name + " " + kw.get('name', ''),
                    'contact_name': kw.get('name', ''),
                    'email_from': kw.get('email', ''),
                    'mobile': kw.get('mobile', ''),
                    'description': kw.get('additional_details', ''),
                    'partner_id': request.env.user.partner_id.id,
                    'property_id': prop.id,
                    'type': 'lead',
                }
                request.env['crm.lead'].sudo().create(lead_data)
        # Find booked properties
        book_prop = request.env['property.bookmark'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)]).mapped('property_id').ids
        # Check already enquiry is submitted or not
        if request.env.user.id != request.env.ref('base.public_user').id:
            lead = request.env['crm.lead'].sudo().search(
                [('partner_id', '=', request.env.user.partner_id.id), ('property_id', '=', prop.id)])
            if lead:
                enquiry_made = True
        # No of bookmarks
        bookmark_count = request.env['property.bookmark'].sudo().search_count([('property_id', '=', prop.id)])
        # context
        config_rec = request.env.ref('tk_website_rental_management.property_theme_config_rec')
        ctx = {
            'prop': prop,
            'book_properties': book_prop,
            'theme_config': config_rec,
            'error_msg': error_msg,
            'enquiry_made': enquiry_made,
            'book_count': bookmark_count,
        }
        return request.render("tk_website_rental_management.property_details", ctx)

    @http.route('/property/wishlist', type='json', auth="user")
    def property_wishlist(self, **kw):
        """User wise wishlist of different property"""
        bookmark_param = request.env['property.bookmark'].sudo()
        property_id = request.env['property.details'].sudo().search([('access_token', '=', kw.get('access'))],
                                                                    limit=1).id
        if property_id:
            toggle = kw.get('toggle')
            bookmark_property = bookmark_param.search([('property_id', '=', property_id),
                                                       ('partner_id', '=',
                                                        request.env.user.partner_id.id)],
                                                      limit=1)
            if toggle and bookmark_property:
                bookmark_property.unlink()
            else:
                bookmark_param.create({'property_id': property_id, 'partner_id': request.env.user.partner_id.id})

        book_prop = bookmark_param.search_count(
            [('partner_id', '=', request.env.user.partner_id.id)])
        return {'count': book_prop}

    @http.route('/property/wishlist/clear', type='json', auth="user")
    def property_wishlist_clear(self, **kw):
        """Clear wishlist of property"""
        bookmark_param = request.env['property.bookmark'].sudo()
        property_id = request.env['property.details'].sudo().search([('access_token', '=', kw.get('access'))],
                                                                    limit=1).id
        if property_id:
            bookmark_property = bookmark_param.search([('property_id', '=', property_id),
                                                       ('partner_id', '=',
                                                        request.env.user.partner_id.id)],
                                                      limit=1)
            if bookmark_property:
                bookmark_property.unlink()
        book_prop = bookmark_param.search_count([('partner_id', '=', request.env.user.partner_id.id)])
        return {'count': book_prop - 1}

    @http.route(['/map-view',
                 '/map-view/page/<int:page>',
                 '/map-view/<string:list_type>',
                 '/map-view/<string:list_type>/page/<int:page>'], type='http', auth="public", website=True)
    def map_view(self, list_type=None, page=0, **kw):
        """List of properties"""
        property_param = request.env['property.details'].sudo()
        # theme config rec
        config_rec = request.env.ref('tk_website_rental_management.property_theme_config_rec')
        # domain list
        list_domain = [('stage', '=', 'available')]
        # category wise filter domain
        if list_type:
            list_domain = list_domain + category_wise_domain_filter(list_type)

        # Property filters
        url_args, prop_filters, default_order = get_all_filters(request.params)
        list_domain = list_domain + prop_filters
        # multi company
        list_domain = list_domain + [('company_id', 'in', [request.website.company_id.id, False])]
        # Dynamic Amenities
        da_list = dynamic_amenities_list(request.params)
        if da_list:
            properties = self.get_dynamic_amenity_filter(da_list)
            list_domain = list_domain + properties

        # property list limit
        property_per_page = config_rec.list_property_per_page
        list_count = property_param.search_count(list_domain)

        # pagination
        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=list_count,
            page=page,
            step=property_per_page,
            url_args=url_args,
        )
        # listings
        listing = property_param.search(list_domain, order=default_order, offset=pager['offset'],
                                        limit=property_per_page)

        book_prop = request.env['property.bookmark'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)]).mapped('property_id').ids

        dynamic_amenity_ids = request.env['property.amenities'].sudo().search([('is_on_website', '=', True)])

        # Categories
        category_domain = []
        if kw.get('categ'):
            category_domain = category_domain + [('type', '=', kw.get('categ'))]
        categories = request.env['property.sub.type'].sudo().search(category_domain, order='sequence asc')

        ctx = {
            'listing': listing,
            'list_type': list_type,
            'pager': pager,
            'cities': property_param.get_all_cities(),
            'theme_config': config_rec,
            'book_properties': book_prop,
            'book_property_count': len(book_prop),
            'da_ids': dynamic_amenity_ids,
            'da_list': da_list,
            'categories': categories,
        }
        return request.render('tk_website_rental_management.map_view', ctx)

    @http.route(['/map/map-view',
                 '/map/map-view/page/<int:page>',
                 '/map/map-view/<string:list_type>',
                 '/map/map-view/<string:list_type>/page/<int:page>',
                 '/map/<string:lang>/map-view',
                 '/map/<string:lang>/map-view/page/<int:page>',
                 '/map/<string:lang>/map-view/<string:list_type>',
                 '/map/<string:lang>/map-view/<string:list_type>/page/<int:page>'], type='json', auth="public",
                website=True, csrf=False)
    def get_properties_by_json(self, list_type=None, lang=None, page=0, **kw):
        property_param = request.env['property.details'].sudo()
        # theme config rec
        config_rec = request.env.ref('tk_website_rental_management.property_theme_config_rec')
        # domain list
        list_domain = [('stage', '=', 'available')]
        # category wise filter domain
        if list_type:
            list_domain = list_domain + category_wise_domain_filter(list_type)

        req_params = {}
        # Property filters
        if kw.get('param', False):
            req_params = convert_str_to_dict(kw.get('param'))
        url_args, prop_filters, default_order = get_all_filters(req_params)
        list_domain = list_domain + prop_filters
        # multi company
        list_domain = list_domain + [('company_id', 'in', [request.website.company_id.id, False])]
        # Dynamic Amenities
        da_list = dynamic_amenities_list(req_params)
        if da_list:
            properties = self.get_dynamic_amenity_filter(da_list)
            list_domain = list_domain + properties

        # property list limit
        property_per_page = config_rec.list_property_per_page
        list_count = property_param.search_count(list_domain)

        # pagination
        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=list_count,
            page=page,
            step=property_per_page,
            url_args=url_args,
        )
        # listings
        list_domain += [('longitude', '!=', False), ('latitude', '!=', False)]
        listing = property_param.search(list_domain, order=default_order, offset=pager['offset'],
                                        limit=property_per_page)
        property_data = []

        for property in listing:
            address = self.get_property_address(property)
            property_class = self.get_property_type(property)
            if property.image:
                property_image = image_data_uri(property.image)
            else:
                property_image = '/tk_website_rental_management/static/src/images/property-placeholder.jpg'
            property_url = '/property-details/' + slug(property)

            if property.sale_lease == 'for_sale':
                property_type = 'Sale'
                property_amount = property.currency_id.symbol + " " + str(property.price)
            else:
                property_type = 'Rent'
                property_amount = property.currency_id.symbol + " " + str(property.price) + " / " + property.rent_unit

            property_data.append((property_url, property_image, property.name, address, property_class, property_amount,
                                  '', property_type,
                                  property.latitude, property.longitude, 0, property_image))

        ctx = {
            'properties': property_data,
            'center': config_rec.map_center_address,
            'latitude': config_rec.latitude,
            'longitude': config_rec.longitude,
            'zoom_level': config_rec.zoom_level,
        }

        return ctx

    def get_property_address(self, property):
        address = ""
        if property.street:
            address += property.street + ", "
        if property.street2:
            address += property.street2 + ", "
        if property.city_id:
            address += property.city_id.name + ", "
        if property.state_id:
            address += property.state_id.code + ", "
        if property.country_id:
            address += property.country_id.code
        return address

    def get_property_type(self, property):
        property_class = ""
        if property.type == 'residential':
            if property.residence_type == 'apartment':
                property_class = 'fa-building'
            else:
                property_class = 'fa-home'
        if property.type == 'land':
            property_class = 'fa-map'
        if property.type == 'commercial':
            property_class = 'fa-dumpster'
        if property.type == 'industrial':
            property_class = 'fa-industry'
        return property_class


class PropertyCustomerPortal(CustomerPortal):
    """Customer portal entry for property enquiry"""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        enquiries = request.env['crm.lead']
        domain = [('partner_id', '=', request.env.user.partner_id.id), ('property_id', '!=', False)]
        values['enquiry_count'] = enquiries.search_count(domain)
        return values

    @http.route(['/property/enquiries'], type='http', auth="user", website=True)
    def property_enquiry_details(self):
        """Get list of property enquiries"""
        enquiries = request.env['crm.lead'].sudo()
        domain = [('partner_id', '=', request.env.user.partner_id.id), ('property_id', '!=', False)]
        recs = enquiries.search(domain)
        ctx = {
            'enqs': recs,
            'page_name': 'enquiry',
        }
        return request.render("tk_website_rental_management.enquiry_list", ctx)

    @http.route(['/property/enquiry/details/<model("crm.lead"):enquiry>'], type='http', auth="user", website=True)
    def portal_my_enquiry_detail(self, enquiry):
        """Return enquiry by property"""
        ctx = {
            'enquiry': enquiry,
            'page_name': 'enquiry',
        }
        return request.render("tk_website_rental_management.enquiry_details", ctx)
