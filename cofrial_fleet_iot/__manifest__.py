{
    "name": "Cofrial - Monitoreo IoT de Flota",
    "summary": "Lecturas simuladas de temperatura, GPS y combustible",
    "version": "19.0.1.6.2",
    "category": "Operations/Fleet",
    "author": "Cofrial SpA - Proyecto Transformacion Digital",
    "license": "LGPL-3",
    "depends": ["base", "fleet"],
    "assets": {
        "web.assets_backend": [
            "cofrial_fleet_iot/static/src/js/vehicle_iot_autorefresh.js",
        ],
    },
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/rules.xml",
        "data/iot_simulator_config.xml",
        "views/views.xml",
        "views/vehicle_monitoring_views.xml",
        "views/vehicle_iot_dashboard.xml",
        "views/iot_simulator_config_views.xml",
        "views/iot_menu_layout.xml",
    ],
    "application": False,
    "installable": True,
}
