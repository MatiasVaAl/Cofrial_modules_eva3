{
    "name": "Cofrial - Inteligencia de Negocios",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "summary": "Dashboard integrado de ventas, CRM e IoT",
    "depends": [
        "web",
        "sale_management",
        "website_sale",
        "crm",
        "cofrial_fleet_iot",
    ],
    "data": [
        "views/bi_dashboard_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cofrial_bi/static/src/js/bi_dashboard.js",
            "cofrial_bi/static/src/xml/bi_dashboard.xml",
        ],
    },
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
