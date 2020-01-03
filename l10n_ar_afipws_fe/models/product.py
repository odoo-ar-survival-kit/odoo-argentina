##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from .pyi25 import PyI25
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO
import logging
import sys
import traceback
from datetime import datetime
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

	codigo_ncm = fields.Char('Codigo NCM')



#class ProductTemplate(models.Model):
#    _inherit = "product.template"
