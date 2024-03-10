# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import requests
import logging

from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class GeoCoder(models.AbstractModel):
    _inherit = "base.geocoder"

    @api.model
    def _call_amap(self, addr, **kw):
        apikey = self.env['ir.config_parameter'].sudo().get_param('amap_geolocalize.amap_api_key')
        if not apikey:
            raise UserError(_(
                "API key for GeoCoding (Places) required.\n"
                "Visit https://lbs.amap.com/api/webservice/create-project-and-key for more information."
            ))
        url = 'http://restapi.amap.com/v3/geocode/geo'
        params = {'address': addr, 'key': apikey}
        try:
            result = requests.get(url, params).json()
        except Exception as e:
            self._raise_query_error(e)

        try:
            if result['count'] == 0:
                return None
            if result['status'] != 1:
                _logger.debug('Invalid Amap call: %s', result['info'])
                error_msg = 'Unable to geolocate, received the error:\n%s' % result['info']
                raise UserError(error_msg)
            location = result['geocodes'][0]['location']
            lng, lat = location.split(',')
            return float(lat, lng)
        except (KeyError, ValueError):
            _logger.debug('Unexcepted Amap API answer.')
