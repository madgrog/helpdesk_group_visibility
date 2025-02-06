{
    "name": "Helpdesk - Group Visibility",
    "version": "0.10",
    "category": "Services/Helpdesk",
    "summary": "Add group membership visibility to Teams and Tickets",
    # "website": "https://github.com/madgrog/pec_manager",
    "website": "",
    "depends": ["helpdesk"],
    "data": [
        'security/group_membership_security.xml',
        # 'security/ir.model.access.csv',
        "views/helpdesk_team_views.xml",
    ],
    "application": False,
    "license": "AGPL-3",
    "author": "Luigi Lamorte",
    "uninstall_hook": "_restore_helpdesk",
}
