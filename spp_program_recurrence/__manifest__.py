# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Program - Recurrence Cycle",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-program",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": ["base", "g2p_programs"],
    "data": ["wizard/program_recurrence.xml", "views/cycle_manager_view.xml"],
    "assets": {},
    "demo": [],
    "images": [],
    "external_dependencies": {
        "python": [
            "python-dateutil",
            "freezegun",
        ]
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}
