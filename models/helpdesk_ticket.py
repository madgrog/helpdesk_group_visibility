import logging
from odoo import models

_logger = logging.getLogger(__name__)

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def test_function(self):
        # result = str(self.env.ref('helpdesk.hr').users.ids).replace('[', '').replace(']', '')
        result = str(self.env.ref('helpdesk.hr').users.partner_id.ids).replace('[', '').replace(']', '')
        return result