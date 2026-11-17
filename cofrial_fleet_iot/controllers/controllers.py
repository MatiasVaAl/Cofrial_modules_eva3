# from odoo import http


# class CofrialFleetIot(http.Controller):
#     @http.route('/cofrial_fleet_iot/cofrial_fleet_iot', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cofrial_fleet_iot/cofrial_fleet_iot/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cofrial_fleet_iot.listing', {
#             'root': '/cofrial_fleet_iot/cofrial_fleet_iot',
#             'objects': http.request.env['cofrial_fleet_iot.cofrial_fleet_iot'].search([]),
#         })

#     @http.route('/cofrial_fleet_iot/cofrial_fleet_iot/objects/<model("cofrial_fleet_iot.cofrial_fleet_iot"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cofrial_fleet_iot.object', {
#             'object': obj
#         })

