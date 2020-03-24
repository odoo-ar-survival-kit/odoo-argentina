##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, api, models
import base64
import logging
_logger = logging.getLogger(__name__)



STEPS = [('1_step','1 step'),('2_step','2 step'),('3_step','3 step'),('4_step','4 step'),('5_step','5 step'),('6_step','6 step'),('end','end')]

class L10nArAfipwsNewCertificate(models.TransientModel):
    _name = 'afipws.new_certificate.wizard'
    _description = 'afipws.new_certificate.wizard'

    @api.model
    def _get_default_env_type(self):
        return self.env['ir.config_parameter'].sudo().get_param('afip.ws.env.type', default='Production')

    state = fields.Selection(
        STEPS,
        string='Step',
        default='1_step'
    )

    certificate_id = fields.Many2one(
        'afipws.certificate_alias',
        readonly=True,
    )
    common_name = fields.Char(
        string='name',
        related = 'certificate_id.common_name'
    )
    env_type = fields.Selection(
        [('production', 'Production'), ('homologation', 'Homologation')],
        'Type',
        default=lambda self: self._get_default_env_type(),
    ) 

    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.user.company_id,
        auto_join=True,
    )

    country_id = fields.Many2one(
        'res.country', 'Country',
    )
    state_id = fields.Many2one(
        'res.country.state', 'State',
    )
    city = fields.Char(
        'City',
    )
    department = fields.Char(
        'Department',
        default='IT',
    )
    cuit = fields.Char(
        'CUIT',
        compute='_compute_cuit',
    )
    company_cuit = fields.Char(
        'Company CUIT',
        size=16,
    )
    service_provider_cuit = fields.Char(
        'Service Provider CUIT',
        size=16,
    )

    service_type = fields.Selection(
        [('in_house', 'In House'), ('outsourced', 'Outsourced')],
        'Service Type',
        default='in_house',
    )
    request_file = fields.Binary(
        'Download Signed Certificate Request',
    )
    request_filename = fields.Char(
        'Filename',
        default="certificate.crs"
    )
    certificate_file = fields.Binary(
        'Upload Certificate',
    )
    journal_code = fields.Char(
        string='Punto de venta',
    )

    afip_ws = fields.Selection(
        [
            ('wsfe', 'Mercado interno -sin detalle- RG2485 (WSFEv1)'),
            ('wsmtxca', 'Mercado interno -con detalle- RG2904 (WSMTXCA)'),
            ('wsfex', 'Exportación -con detalle- RG2758 (WSFEXv1)'),
            ('wsbfe', 'Bono Fiscal -con detalle- RG2557 (WSBFE)'),
        ],
        'AFIP WS',
        default = 'wsfe'
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='journal',
    )
    @api.onchange('env_type')
    def _onchange_env_type(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'afip.ws.env.type', self.env_type)

    @api.depends('company_cuit', 'service_provider_cuit', 'service_type')
    def _compute_cuit(self):
        for rec in self:
            if rec.service_type == 'outsourced':
                rec.cuit = rec.service_provider_cuit
            else:
                rec.cuit = rec.company_cuit

    @api.onchange('company_id')
    def change_company_id(self):
        if self.company_id:
            self.country_id = self.company_id.country_id.id
            self.state_id = self.company_id.state_id.id
            self.city = self.company_id.city
            self.company_cuit = self.company_id.vat

    def next_step(self):
        max_step = len(STEPS)
        step = next((i for i,x in enumerate(STEPS) if self.state in x[0]),0)
        if step < max_step:
            self.state=STEPS[step+1][0]
    def prev_step(self):
        step = next((i for i,x in enumerate(STEPS) if self.state in x[0]),0)
        if len(self.certificate_id )== 0:
            min_state= 0
        elif self.certificate_id.state == 'draft':
            min_state= 2
        else :
            min_state= 4
        if step > min_state:
            self.state=STEPS[step-1][0]
    def write(self,values):
        res = super(L10nArAfipwsNewCertificate,self).write(values)
        if 'state' in values and values['state']=='4_step':
            cert_values = {
                'type':self.env_type,
                'company_id':self.company_id.id,
                'country_id':self.country_id.id,
                'state_id':self.state_id.id,
                'city':self.city,
                'department':self.department,
                'cuit':self.cuit,
                'company_cuit':self.company_cuit,
                'service_provider_cuit':self.service_provider_cuit,
                'service_type':self.service_type,
            }
            if len(self.certificate_id):
                self.certificate_id.write(cert_values)
            else :
                certificate_id = self.env['afipws.certificate_alias'].create(cert_values)
                self.certificate_id = certificate_id.id
            self.certificate_id.change_company_name()
            self.certificate_id.action_confirm()
            self.certificate_id.action_create_certificate_request()
            self.request_file = self.certificate_id.certificate_ids[0].request_file
        if 'state' in values and values['state']=='6_step':
            self.certificate_id.certificate_ids[0].write(
                {'crt': base64.decodestring(self.certificate_file)})
            self.certificate_id.certificate_ids[0].action_confirm()
        if 'state' in values and values['state']=='end':
            pos_number = int(self.journal_code)

            journal = {
                'name':'{:03d}'.format(pos_number),
                'type':'sale',
                'l10n_latam_use_documents':True,
                'l10n_ar_afip_pos_system':'RLI_RLM',
                'l10n_ar_afip_pos_number':pos_number,
                'l10n_ar_afip_pos_partner_id':self.company_id.partner_id.id,
                'afip_ws':self.afip_ws,
                'code':'s{:03d}'.format(pos_number),
                'invoice_reference_type':'invoice',
                'invoice_reference_model':'odoo',

            }
            journal_id = self.env['account.journal'].create(journal)
            journal_id.action_get_connection()
            journal_id.sync_document_local_remote_number()
            self.journal_id = journal_id

            

        return res