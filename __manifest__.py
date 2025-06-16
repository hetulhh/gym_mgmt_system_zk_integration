# -*- coding: utf-8 -*-
# More info at https://www.odoo.com/documentation/master/reference/module.html

{
    "name": "Gym Management ZK Integration",
    "depends": [
        "base",
        "gym_mgmt_system",
    ],
    "data": [
        "security/gym_mgmt_system_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/gym_mgmt_system_zk_integration_sequence.xml",
        'views/members.xml',
        'views/zk_machine_view.xml',
        'wizards/device_selection_views.xml',
        'wizards/membership_invoice_views.xml',
    ],
    "application": False,
    "license": "LGPL-3",
}
