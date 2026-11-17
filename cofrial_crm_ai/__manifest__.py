{
    'name': 'Cofrial - Clasificacion IA CRM',
    'version': '19.0.1.0.0',
    'summary': 'Clasificacion inteligente de consultas comerciales',
    'author': 'Equipo COFRIAL - INACAP',
    'category': 'Sales/CRM',
    'depends': ['base', 'crm'],
    'data': [
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
        'data/ai_categories.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
