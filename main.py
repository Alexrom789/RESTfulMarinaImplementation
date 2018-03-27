# Author: Alejandro Romero
# RESTful Marina Implementation

from google.appengine.ext import ndb
import webapp2
import json

class Boat(ndb.Model):
    id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=True)
    length = ndb.IntegerProperty(required=True)
    at_sea = ndb.BooleanProperty()

class BoatHandler(webapp2.RequestHandler):
    def post(self):
        post_data = json.loads(self.request.body)
        input_name = False
        input_type = False
        input_length = False
        for item in post_data:
            if item == "name":
                input_name = True
            elif item == "type":
                input_type = True
            elif item == "length":
                input_length = True
        if input_name and input_type and input_length:
            post_boat = Boat(name=post_data['name'],
                             type=post_data['type'],
                             length=post_data['length'])
            post_boat.at_sea = True
            post_boat.put()
            post_boat.id = str(post_boat.key.urlsafe())
            post_boat.put()
            post_boat_dict = post_boat.to_dict()
            post_boat_dict['self'] = '/boats/' + post_boat.key.urlsafe()
            self.response.write(json.dumps(post_boat_dict))
        else:
            self.response.status = 400
            self.response.write("Request failed. Use the following format: {\"name\": \"str\", \"type\": \"str\", \"length\": int}")


    def get(self, id=None):
        if id:
            boat_exists = False
            for boat in Boat.query():
                if boat.id == id:
                    boat_exists = True
            if boat_exists:
                get_boat = ndb.Key(urlsafe=id).get()
                get_boat_dict = get_boat.to_dict()
                get_boat_dict['self'] = "/boats/" + id
                self.response.write(json.dumps(get_boat_dict))
            else:
                self.response.status = 400
                self.response.write("No such boat in the Marina")
        else:
            get_boat_query_results = [get_boat_query.to_dict()
                                      for get_boat_query in Boat.query()]
            for boat in get_boat_query_results:
                boat['self'] = "/boats/" + str(boat['id'])
            self.response.write(json.dumps(get_boat_query_results))

    def delete(self, id=None):
        if id:
            boat_exists = False
            for boat in Boat.query():
                if boat.id == id:
                    boat_exists = True
            if boat_exists:
                reset_slip = False
                for slip in Slip.query(Slip.current_boat == id):
                    if slip.current_boat and slip.arrival_date:
                        slip.current_boat = ""
                        slip.arrival_date = ""
                        slip.put()
                        reset_slip = True

                if reset_slip:
                    ndb.Key(urlsafe=id).delete()
                    self.response.write("Boat was successfully deleted and removed from slip")
                else:
                    ndb.Key(urlsafe=id).delete()
                    self.response.write("Boat was successfully deleted")
            else:
                self.response.status = 400
                self.response.write("No such boat in the Marina")

    def patch(self, id=None):
        if id:
            patch_boat_data = json.loads(self.request.body)
            boat_exists = False
            for boat in Boat.query():
                if boat.id == id:
                    boat_exists = True
            if boat_exists:
                patch_boat = ndb.Key(urlsafe=id).get()
                if len(patch_boat_data) > 1:
                    self.response.status = 400
                    self.response.write("Request failed. Use the following format: {\"name\": \"str\"}  or {\"type\": \"str\"} or {\"length\": int}")
                else:
                    for key in patch_boat_data:
                        if key == "name":
                            patch_boat.name = patch_boat_data['name']
                            patch_boat.put()
                            self.response.write("The boat's 'name' was successfully updated")
                        elif key == "type":
                            patch_boat.type = patch_boat_data['type']
                            patch_boat.put()
                            self.response.write("The boat's 'type' was sucessfully updated")
                        elif key == "length":
                            patch_boat.length = patch_boat_data['length']
                            patch_boat.put()
                            self.response.write("The boat's 'length' was successfully updated")
                        else:
                            self.response.status = 400
                            self.response.write("Request failed. Use the following format: {\"name\": \"str\"}  or {\"type\": \"str\"} or {\"length\": int}")
            else:
                self.response.status = 400
                self.response.write("No such boat in the Marina")

    def put(self, id=None):
        if id:
            put_boat_data = json.loads(self.request.body)
            boat_exists = False
            for boat in Boat.query():
                if boat.id == id:
                    boat_exists = True
            if boat_exists:
                put_boat = ndb.Key(urlsafe=id).get()
                input_name = False
                input_type = False
                input_length = False
                for item in put_boat_data:
                    if item == "name":
                        input_name = True
                    elif item == "type":
                        input_type = True
                    elif item == "length":
                        input_length = True
                if input_name and input_type and input_length:
                    put_boat.name = put_boat_data['name']
                    put_boat.type = put_boat_data['type']
                    put_boat.length = put_boat_data['length']
                    put_boat.put()
                    self.response.write("The boat's 'name', 'type', and 'length' were successfully updated")
                else:
                    self.response.status = 400
                    self.response.write("Request failed. Use the following format: {\"name\": \"str\", \"type\": \"str\", \"length\": int}")
            else:
                self.response.status = 400
                self.response.write("No such boat in the Marina")

class Slip(ndb.Model):
    id = ndb.StringProperty()
    number = ndb.IntegerProperty(required=True)
    current_boat = ndb.StringProperty(required=True)
    arrival_date = ndb.StringProperty(required=True)

class SlipHandler(webapp2.RequestHandler):
    def post(self):
        post_slip_data = json.loads(self.request.body)
        post_slip_query_results = [post_slip_query.to_dict()
                                  for post_slip_query in Slip.query()]
        input_number = False
        for item in post_slip_data:
            if item == "number":
                input_number = True
        if input_number:
            in_use = False
            for slip in post_slip_query_results:
                if slip['number'] == post_slip_data['number']:
                    in_use = True
                    self.response.status = 403
                    self.response.write("Request failed. Slip number is already in use.")
            if not in_use:
                post_slip = Slip(number=post_slip_data['number'])
                post_slip.current_boat = ""
                post_slip.arrival_date = ""
                post_slip.put()
                post_slip.id = str(post_slip.key.urlsafe())
                post_slip.put()
                post_slip_dict = post_slip.to_dict()
                post_slip_dict['self'] = '/slips/' + post_slip.key.urlsafe()
                self.response.write(json.dumps(post_slip_dict))
        else:
            self.response.status = 400
            self.response.write("Request failed. Use the following format {\"number\": int}")

    def get(self, id=None):
        if id:
            slip_exists = False
            for slip in Slip.query():
                if slip.id == id:
                    slip_exists = True
            if slip_exists:
                get_slip = ndb.Key(urlsafe=id).get()
                get_slip_dict = get_slip.to_dict()
                get_slip_dict['self'] = "/slips/" + id
                self.response.write(json.dumps(get_slip_dict))
            else:
                self.response.status = 400
                self.response.write("No such slip in the Marina")
        else:
            get_slip_query_results = [get_slip_query.to_dict()
                                      for get_slip_query in Slip.query()]
            for slip in get_slip_query_results:
                slip['self'] = "/slips/" + str(slip['id'])
            self.response.write(json.dumps(get_slip_query_results))

    def delete(self, id=None):
        if id:
            slip_exists = False
            for slip in Slip.query():
                if slip.id == id:
                    slip_exists = True
            if slip_exists:
                delete_slip = ndb.Key(urlsafe=id).get()
                if delete_slip.current_boat:
                    boat_in_the_slip = ndb.Key(urlsafe=delete_slip.current_boat).get()
                    boat_in_the_slip.at_sea = True;
                    boat_in_the_slip.put()
                    delete_slip.key.delete()
                    self.response.write("Slip was successfully deleted and boat was sent out to sea")
                else:
                    delete_slip.key.delete()
                    self.response.write("Slip was successfully deleted")
            else:
                self.response.status = 400
                self.response.write("No such slip in the Marina")

    def patch(self, id=None):
        if id:
            patch_slip_data = json.loads(self.request.body)
            slip_exists = False
            for slip in Slip.query():
                if slip.id == id:
                    slip_exists = True
            if slip_exists:
                patch_slip = ndb.Key(urlsafe=id).get()
                if len(patch_slip_data) > 1:
                    self.response.status = 400
                    self.response.write("Request failed. Use the following format: {\"number\": int}")
                else:
                    for key in patch_slip_data:
                        if key == "number":
                            patch_slip_query_results = [patch_slip_query.to_dict()
                                                      for patch_slip_query in Slip.query()]
                            found_it = False
                            for slip in patch_slip_query_results:
                                if slip['number'] == patch_slip_data['number']:
                                    found_it = True
                                    self.response.status = 403
                                    self.response.write("Request failed. Slip number is already in use.")
                            if not found_it:
                                patch_slip.number = patch_slip_data['number']
                                patch_slip.put()
                                self.response.write("The slip's 'number' was successfully updated")
                        else:
                            self.response.status = 400
                            self.response.write("Request failed. Use the following format {\"number\": int}")
            else:
                self.response.status = 400
                self.response.write("No such slip in the Marina")

class BoatInSlipHandler(webapp2.RequestHandler):
    def get(self, id=None):
        if id:
            slip_exists = False
            for slip in Slip.query():
                if slip.id == id:
                    slip_exists = True
            if slip_exists:
                get_slip = ndb.Key(urlsafe=id).get()
                if get_slip.current_boat == "":
                    self.response.write("Request failed. Slip is empty.")
                else:
                    get_boat = ndb.Key(urlsafe=get_slip.current_boat).get()
                    boat_dict = get_boat.to_dict()
                    boat_dict['self'] = "/boats/" + get_slip.current_boat
                    self.response.write(json.dumps(boat_dict))
            else:
                self.response.status = 400
                self.response.write("No such slip in the Marina")

    def put(self, id=None):
        if id:
            put_data = json.loads(self.request.body)
            slip_exists = False
            for slip in Slip.query():
                if slip.id == id:
                    slip_exists = True
            if slip_exists:
                put_slip = ndb.Key(urlsafe=id).get()
                input_current_boat = False
                input_arrival_date = False
                for item in put_data:
                    if item == "current_boat":
                        input_current_boat = True
                    elif item == "arrival_date":
                        input_arrival_date = True
                if input_current_boat and input_arrival_date:
                    boat_exists = False
                    for boat in Boat.query():
                        if boat.id == put_data['current_boat']:
                            boat_exists = True
                    if boat_exists:
                        put_boat = ndb.Key(urlsafe=put_data['current_boat']).get()
                        if put_boat.at_sea:
                            if put_slip.current_boat == "":
                                put_slip.current_boat = put_data['current_boat']
                                put_slip.arrival_date = put_data['arrival_date']
                                put_slip.put()
                                put_boat.at_sea = False
                                put_boat.put()
                                self.response.write("Boat was successfully added to slip and docked.")
                            else:
                                self.response.status = 403
                                self.response.write("Request failed. slip already occupied")
                        else:
                            self.response.status = 403
                            self.response.write("Request failed. Boat is already in a slip")
                    else:
                        self.response.status = 400
                        self.response.write("No such boat in the Marina")
                else:
                    self.response.status = 400
                    self.response.write("Request failed. Use the following format. {\"current_boat\": \"boat_id\", \"arrival_date\": \"YYYY-MM-DD\"}")
            else:
                self.response.status = 400
                self.response.write("No such slip in the Marina.")

    def delete(self, id=None):
        if id:
            slip_exists = False
            for slip in Slip.query():
                if slip.id == id:
                    slip_exists = True
            if slip_exists:
                slip = ndb.Key(urlsafe=id).get()
                if slip.current_boat:
                    boat_in_slip = ndb.Key(urlsafe=slip.current_boat).get()
                    boat_in_slip.at_sea = True
                    boat_in_slip.put()
                    slip.current_boat = ""
                    slip.arrival_date = ""
                    slip.put()
                    self.response.write("Boat was successfully removed from slip and sent out to sea")
                else:
                    self.response.status = 403
                    self.response.write("Request failed. Slip is empty")
            else:
                self.response.status = 400
                self.response.write("No such slip in the Marina")

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("Welcome to Alejandro Romero's Marina REST project.")

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boats',BoatHandler),
    ('/boats/(.*)',BoatHandler),
    ('/slips',SlipHandler),
    ('/slips/(.*)/boat',BoatInSlipHandler),
    ('/slips/(.*)',SlipHandler)
], debug=True)