# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Albin P J(odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CourierDistancePrice(models.Model):
    """This is for creating courier distance price rule"""
    _name = 'courier.distance.price'
    _description = "Courier Distance PriceRule"

    name = fields.Char(string="Name", required=True,
                       help="Name of courier distance price rule")
    minimum_distance = fields.Float(string="Minimum Distance", required=True,
                                    help="Minimum distance for delivery")
    maximum_distance = fields.Float(string="Maximum Distance", required=True,
                                    help="Maximum distance for delivery")
    company_id = fields.Many2one('res.company', string="Company",
                                 required=True,
                                 default=lambda self: self.env.company,
                                 readonly=True, help="Current company")
    currency_id = fields.Many2one("res.currency", string='Currency',
                                  related='company_id.currency_id',
                                  help="Company currency")
    price = fields.Monetary(string="Price", required=True,
                            help="Price based on the distance")

    @api.constrains('maximum_distance', 'minimum_distance')
    def _check_distance(self):
        """Returns validation based on distance"""
        if self.minimum_distance <= 0 or self.maximum_distance <= 0:
            raise ValidationError(_('Delivery is not possible'))
        if self.minimum_distance == 0 or self.maximum_distance == 0:
            raise ValidationError(_('Invalid Distance'))
        if self.minimum_distance > self.maximum_distance:
            raise ValidationError(
                _('Minimum Distance must be less than Maximum Distance'))
