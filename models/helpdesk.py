import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    # department_id = fields.Many2one('hr.department', string='Department', help="The Department of the Team.")
    group_id = fields.Many2one('res.groups', string='Group', help="User group that can access this Team.")
    privacy_visibility = fields.Selection(
        selection_add=[('group', 'Invited portal users and internal users members of selected user group')],
        ondelete={'group': 'set default'}, help="People to whom this helpdesk team and its tickets will be visible.\n\n"
        "- Invited internal users: internal users can access the team and the tickets they are following. "
        "This access can be modified on each ticket individually by adding or removing the user as follower.\n"
        "A user with the helpdesk > administrator access right level can still access this team and its tickets, even if they are not explicitely part of the followers.\n\n"
        "- All internal users: all internal users can access the team and all of its tickets without distinction.\n\n"
        "- Invited portal users and all internal users: all internal users can access the team and all of its tickets without distinction.\n"
        "Portal users can only access the tickets they are following. "
        "This access can be modified on each ticket individually by adding or removing the portal user as follower."
        "... add description for group selection ..."
    )

    @api.constrains('use_website_helpdesk_form', 'privacy_visibility')
    def _check_website_privacy(self):
        """
        Override original function to support new group privacy visibility.
        """
        if any(t.use_website_helpdesk_form and t.privacy_visibility not in ['portal', 'group'] for t in self):
            raise ValidationError(_('The visibility of the team needs to be set as one of two "Invited portal users..." options in order to use the website form.'))

    @api.depends('privacy_visibility')
    def _compute_privacy_visibility_warning(self):
        """
        Override original function to support new group privacy visibility.
        """
        for team in self:
            if not team.ids:
                team.privacy_visibility_warning = ''
            elif team.privacy_visibility in ['portal', 'group'] and team._origin.privacy_visibility not in ['portal', 'group']:
                team.privacy_visibility_warning = _('Customers will be added to the followers of their tickets.')
            elif team.privacy_visibility not in ['portal', 'group'] and team._origin.privacy_visibility in ['portal', 'group']:
                team.privacy_visibility_warning = _('Portal users will be removed from the followers of the team and its tickets.')
            else:
                team.privacy_visibility_warning = ''

    @api.depends('privacy_visibility')
    def _compute_access_instruction_message(self):
        """
        Override original function to support new group privacy visibility.
        """
        for team in self:
            if team.privacy_visibility == 'group':
                team.access_instruction_message = _('Grant portal users access to your helpdesk team or tickets by adding them as followers.')
            else:
                super(HelpdeskTeam, self)._compute_access_instruction_message()

    def _change_privacy_visibility(self, new_visibility):
        """
        Unsubscribe non-internal users from the team and tickets if the team privacy visibility
        goes from 'portal' or 'group' to a different value.
        If the privacy visibility is set to 'portal', subscribe back tickets partners.
        """
        for team in self:
            if team.privacy_visibility == new_visibility:
                continue
            if new_visibility in ['portal', 'group']:
                for ticket in team.mapped('ticket_ids').filtered('partner_id'):
                    ticket.message_subscribe(partner_ids=ticket.partner_id.ids)
            elif team.privacy_visibility in ['portal', 'group']:
                portal_users = team.message_partner_ids.user_ids.filtered('share')
                team.message_unsubscribe(partner_ids=portal_users.partner_id.ids)
                team.mapped('ticket_ids')._unsubscribe_portal_users()
