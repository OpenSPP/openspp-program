# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Programs: Compliance Criteria",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-program",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123", "nhatnm0612"],
    "depends": [
        "spp_programs",
        "queue_job",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "views/g2p_program_views.xml",
        "wizards/g2p_program_create_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/spp_programs_compliance_criteria/static/src/js/list_view_buttons.js",
        ],
        "web.assets_qweb": [
            "/spp_programs_compliance_criteria/static/src/xml/list_view_buttons.xml",
        ],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
}
