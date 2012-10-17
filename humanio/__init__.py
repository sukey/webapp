# Copyright 2012 Tasty Labs

"""
Human.io is an API that lets you create lightweight apps for mobile
devices, and push those apps onto specific users that meet your
criteria (e.g., your app should only appear for users in New York, or
to mobile devices with a camera).

Our "Hello, World"::

    import humanio

    app = humanio.App(my_developer_id, my_secret_key)

    def on_connect(session, task, item):
        session.add_text("Hello, world")
        session.add_submit_button("OK")

    def on_submit(session, task, form_data):
        session.dismiss(approve=True)
        task.app.stop_loop()

    task = app.create_task(description="Hello, world", humans_per_item=1,
                           on_connect_fn=on_connect, on_submit_fn=on_submit)
    app.start_loop()

Learn more about the human.io API `here <http://human.io/docs>`_, and
start writing applications with our `Getting Started
<http://human.io/docs/getting_started>`_ guide.

.. _tornado library: http://tornadoweb.org
"""

import json
import os
import time
import urllib
import urllib2
import httplib
import base64

FORM_NAME_KEY = "__form_name__"

class App(object):
    """
    Main class for a Human.io application.
    """
    def __init__(self, developer_id, secret_key, app_id=None,
                 public=False, callback_url=None, register_with_server=True):
        """
        Instantiates a human.io App.  With this app, you can create any number of Tasks, which is what people actually see and connect to on their client screen.

        :param developer_id: Developer ID as created at http://human.io/developer
        :param secret_key: Your secret key, as returned by http://human.io/developer when you created your account.
        :param app_id: You can optionally supply a string to identify this app by.  The string is namespaced to your developer account, so it will not conflict with other developer's.  If you do not provide an app_id, a random app_id will be generated.
        :type app_id: string or None
        :param public: If not public, this app's tasks will only be visible to clients which are following this developer_id.
        :type public: bool
        :param callback_url: The server will call this URL upon receiving an event.
        :type callback_url: string
        :param register_with_server: Whether to register this app with the human.io server.
            This defaults to True, which is nearly always what you want. Use False if you
            know that the app is already registered.
        :type register_with_server: bool
        """

        server_host = os.getenv("HUMANIO_HOST", "api.human.io")
        server_port = os.getenv("HUMANIO_PORT", "80")

        self.developer_id = developer_id
        self.secret_key = secret_key

        if not public:
            print """\
-- You've marked this app is private (public=False).
-- You won't see it in the client by default. If using the web client,
-- be sure to sign in first at http://human.io/developer. If using your phone,
-- be sure to follow your own developer account: http://human.io/developer
"""

        self.server_url = "http://%s:%s" % (server_host, server_port)

        params = {}
        if callback_url:
            params["callback_url"] = callback_url
        if app_id:
            params["app_id"] = app_id
            self.app_id = app_id

        params["public"] = int(bool(public))

        if register_with_server:
            req = self._call_api("app", params)

            if req["status_code"] != 200:
                raise Exception("api connect call failed (code %d): url=%s message='%s'" %
                                (req["status_code"], req["url"], req["text"]))
            response = json.loads(req["text"])
            self.app_id = response["app_id"]

        self.callback_url = callback_url
        self.tasks = {}

    def delete(self):
        """
        Delete this app on the server. This object must not be used after
        calling this method.
        """

        self._call_api("app/%s/delete" % self.app_id, {})

    def _call_api(self, method_name, params):
        url, body, headers = self._get_fetch_parameters(method_name, params)

        obj = {
            "url": url,
            "text": "(no message)",
            "status_code": -1,
        }
        try:
            request = urllib2.Request(url, data=body, headers=headers)
            f = urllib2.urlopen(request)

            obj["text"] = f.read()
            obj["status_code"] = f.code
        except urllib2.HTTPError as e:
            # The "e" object behaves like "f" above.
            obj["status_code"] = e.code
            obj["text"] = e.read()
        except urllib2.URLError as e:
            obj["status_code"] = -2
            obj["text"] = e.reason
        except httplib.BadStatusLine as e:
            # The human.io server restarted.
            obj["status_code"] = -3
            obj["text"] = str(e) or str(type(e))
        except httplib.HTTPException as e:
            obj["status_code"] = -4
            obj["text"] = str(e) or str(type(e))

        return obj

    def create_task(self, task_id=None, description=None, hidden=False, thumbnail=None,
            items=None, humans_per_item=1, auto_repeat=None, human_can_do_multiple=False,
            latitude=None, longitude=None, radius_miles=None, camera=False,
            on_connect_fn=None, on_finished_fn=None, on_disconnect_fn=None,
            on_submit_fn=None, on_submit_fns=None, register_with_server=True):
        """
        Create a Task that people can connect to.  This requests people that meet certain criteria; it can pass them some initial data; and it specifies the python function callbacks to invoke as people make their way through the task.

        :param task_id: The ID of the task to create. If not specified, a random unique string is generated. For demos and tests this parameter can be left out, but for real apps it should be specified so that the data on the server can persist when re-connecting the app.
        :param description: Description of the task or activity.  This is shown in people's client app.
        :param hidden: If hidden, the task description does not appear in any client app.
        :param thumbnail: An image to display on the iOS and Android app's Activities page.
        :param items: A list of objects to use as data items. If this is left out then a single empty object is used. Data items are passed one at a time to the connection callback. This can also be an empty list and data can be added later (in REST by posting to the task, or in the Python API by calling add_items()). This must be a list or a TypeError is raised.
        :param humans_per_item: How many people you are requesting.  Specify -1 for unlimited number.
        :param auto_repeat: When a user finishes the work for a data item, they normally get sent back to the main menu. If this flag is set, the user will instead be shown another data item, which they can cancel out of. This is useful for quick items.
        :param human_can_do_multiple: Whether the same human can get the same item more than once. By default this is false and a data item won't be given to the same human multiple times.
        :param camera: Request only people who have cameras on the client app device.
        :param latitude: Requesting people this latitude.  Longitude must also be specified.
        :param longitude: Requesting people near this longitude.  Latitude must also be specified.
        :param radius_miles: Required proximity to (latitude, longitude).  Default is 15.
        :param on_connect_fn: Function to call when a user connects. This is the only
            required callback parameter. The function is passed three parameters:
            A ``Session`` object, this ``Task`` object, and a data item from your list of items.
        :param on_finished_fn: Optional function to call when all data items have had
            all the humans they need. This is never called if humans_per_item is -1.
            The function is passed one parameter: the ``Task``.
        :param on_disconnect_fn: Optional function to call when the human disconnects
            part-way through a task. Passed a ``Session`` object and this ``Task``.
        :param on_submit_fn: Optional function to call when the human submits any form.
            Passed a ``Session`` object, this ``Task``, and a dictionary of name/value pairs
            from the form.
        :param on_submit_fns: Optional dictionary mapping form names to functions. When a form
            is submitted by the human, if it has a name as provided by ``set_form_name()``
            or designated by the on_submit parameter to add_submit_button() or
            add_list_submit_button(), the name will be looked up in this dictionary. If the name is
            found, its function will be called. If not, then the function provided by
            ``on_submit_fn`` will be called. The function takes the same arguments as
            ``on_submit_fn``.
        :param register_with_server: Whether to register this task with the human.io server.
            This defaults to True, which is nearly always what you want. Use False if you
            know that the task is already registered.
        :type register_with_server: bool

        :return: A Task object, with the fields "url", and "task_hashed_id"
        """

        assert on_connect_fn

        if items is not None and not isinstance(items, list):
            raise TypeError("items must be a list")

        task = Task(task_id, self, description, humans_per_item, items, on_connect_fn,
                on_finished_fn, on_disconnect_fn, on_submit_fn, on_submit_fns, hidden,
                camera, latitude, longitude, radius_miles, auto_repeat, human_can_do_multiple,
                thumbnail)
        if register_with_server:
            task._register_with_server()

        self.tasks[task.task_id] = task

        return task

    def add_items(self, task_id, items):
        """
        Add one or more data items to an existing Task.

        :param task_id: The ID of the task to add data items to.
        :type task_id: string
        :param items: Data items to add to task. This must be a list or a TypeError is raised. See description of items in ``create_task()`` in :py:class:`App`
        :type items: list of items
        """
        if not isinstance(items, list):
            raise TypeError("items must be a list")

        params = {
            "app_id": self.app_id,
            "items": json.dumps(items),
        }
        self._call_api("task/%s" % task_id, params)

    def delete_task(self, task_id):
        """
        Delete the specified task on the server.

        :param task_id: The ID of the task to delete.
        :type task_id: string
        """

        params = {
            "app_id": self.app_id,
        }
        self._call_api("task/%s/delete" % task_id, params)

        # Remove from our data structures.
        self.tasks.pop(task_id, None)

    def handle_response(self, response_json):
        """
        Call this when your callback-URL (web hook) app receives a
        message from the server. This may dispatch one of your task
        callback functions.

        :param response_json: the raw string of the body of the POST.
        """
        response = json.loads(response_json)
        status = response["status"]
        if status == "error":
            print "Error status:", response
        else:
            event_name = response["event_name"]
            if event_name == "human_connected":
                session_id = response["session_id"]
                task_id = response["task_id"]
                item = response["item"]
                human = response.get("human")
                task = self.tasks.get(task_id)
                if task:
                    task._human_connected(session_id, item, human)
                else:
                    print "human_connected: Unknown task ID %s" % task_id
            elif event_name == "human_disconnected":
                session_id = response["session_id"]
                task_id = response["task_id"]
                human = response.get("human")
                task = self.tasks.get(task_id)
                if task:
                    task._human_disconnected(session_id, human)
                else:
                    print "human_disconnected: Unknown task ID %s" % task_id
            elif event_name == "human_submitted":
                session_id = response["session_id"]
                task_id = response["task_id"]
                values = response["values"]
                human = response.get("human")
                task = self.tasks.get(task_id)
                if task:
                    task._human_submitted(session_id, values, human)
            elif event_name == "task_finished":
                task_id = response["task_id"]
                task = self.tasks.get(task_id)
                if task and task.on_finished_fn:
                    task.on_finished_fn(task)
            elif event_name == "ping":
                # Nothing to do.
                pass
            else:
                print "Unknown event_name: %s" % event_name

    def _get_fetch_parameters(self, method_name, params):
        # Make copy.
        params = dict(params)

        url = self.server_url + "/v1/" + method_name

        # We prefer Basic authentication (see "Authorization" header below) but are keeping
        # these two lines around in case the developer is hitting an older server.
        params["developer_id"] = self.developer_id
        params["secret_key"] = self.secret_key

        # Make a text version of the body.
        body = urllib.urlencode(params)

        headers = {
            # Neither the developer ID nor the secret key contains a colon.
            "Authorization": base64.b64encode(self.developer_id + ":" + self.secret_key)
        }

        return url, body, headers

    def start_loop(self):
        """Starts the loop to fetch events from the server. Does not return until
        stop_loop() is called. Uses the urllib2 module to make blocking calls to
        the server."""

        if self.callback_url:
            raise Exception("Cannot call start_loop() when callback_url was specified")

        self.running = True
        while self.running:
            params = {
                "app_id": self.app_id,
            }
            results = self._call_api("next_event", params)
            if results["status_code"] == 200:
                self.handle_response(results["text"])
            elif results["status_code"] == 504:
                # 504 Gateway Timeout. Nginx timed out. This isn't a
                # problem, just try again. No need to sleep here.
                pass
            elif results["status_code"] == -3 or results["status_code"] == 502:
                # The human.io server restarted. Sleep quietly.
                time.sleep(1)
            else:
                # Sleep and try again.
                print "Got code %d (%s) getting next event" % (results["status_code"],
                        results["text"])
                time.sleep(1)

    def stop_loop(self):
        """Stops the loop started by start_loop. Only works if start_loop() is calling
        a callback function. Can't be called from another thread to asynchronously
        stop the loop."""

        if self.callback_url:
            raise Exception("Cannot call start_loop() when callback_url was specified")

        self.running = False


class AppTornado(App):
    """Version of the App class for use with the Tornado web framework. The Tornado
    framework is asynchronous, so we use the asynchronous version of the HTTP client
    to fetch commands from the server."""

    def start_loop(self):
        """Starts the Tornado IOLoop instance."""

        if self.callback_url:
            raise Exception("Cannot call start_loop() when callback_url was specified")

        self._fetch_response()

        import tornado.ioloop
        tornado.ioloop.IOLoop.instance().start()

    def start_connection(self):
        """
        Like start_loop(), but called when the app has its own main loop.
        """
        self._fetch_response()

    def stop_loop(self):
        """Stops the Tornado IOLoop instance."""

        if self.callback_url:
            raise Exception("Cannot call start_loop() when callback_url was specified")

        import tornado.ioloop
        tornado.ioloop.IOLoop.instance().stop()

    def run_delayed(self, delay_s, fn):
        """
        Call the function after a certain number of seconds. Uses the Tornado
        add_timeout() function to asynchronously call a function.

        :param delay_s: Delay, in seconds.
        :type delay_s: float
        :param fn: Function to call after 'delay_s' seconds. Takes no parameters.
        """
        import tornado.ioloop
        tornado.ioloop.IOLoop.instance().add_timeout(time.time() + delay_s, fn)

    def _fetch_response(self):
        params = {
            "app_id": self.app_id,
        }
        url, body, headers = self._get_fetch_parameters("next_event", params)

        import tornado.httpclient
        request = tornado.httpclient.HTTPRequest(url=url,
                                                 method="POST",
                                                 request_timeout=600,
                                                 headers=headers,
                                                 body=body)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(request, self._fetch_response_callback)

    def _fetch_response_callback(self, http_response):
        if http_response.error:
            # 599 is timeout. Don't print the error in that case.
            if http_response.code != 599:
                print "Error:", http_response.error
            time.sleep(1)
        else:
            self.handle_response(http_response.body)

        # Get the next one.
        self._fetch_response()


class Task(object):
    def __init__(self, task_id, app, description, humans_per_item, items,
            on_connect_fn, on_finished_fn, on_disconnect_fn, on_submit_fn, on_submit_fns,
            hidden, camera, latitude, longitude, radius_miles, auto_repeat, human_can_do_multiple,
            thumbnail):
        """
        A Task object.  This should not be instantiated directly, but
        only by the ``create_task()`` method of App.

        Member variables:

        * task_id: An ID string identifying this task
        * url: The direct-access URL for this task.  The URL points to a page on http://human.io which first prompts the user to install the human.io client if they are on mobile, and then gives either a "Go To" pairing code or button to immediately start running this task on the mobile app.
        """

        self.task_id = task_id
        self.task_hashed_id = None
        self.app = app
        self.description = description
        self.humans_per_item = humans_per_item
        self.items = items
        self.on_connect_fn = on_connect_fn
        self.on_finished_fn = on_finished_fn
        self.on_disconnect_fn = on_disconnect_fn
        self.on_submit_fn = on_submit_fn
        self.on_submit_fns = on_submit_fns
        self.hidden = hidden
        self.camera = camera
        self.latitude = latitude
        self.longitude = longitude
        self.radius_miles = radius_miles
        self.auto_repeat = auto_repeat
        self.human_can_do_multiple = human_can_do_multiple
        self.url = ""
        self.thumbnail = thumbnail

    def add_items(self, items):
        """
        Add one or more data items to a Task.

        :param items: Data items to add to task.  See description of items in ``create_task()`` in :py:class:`App`
        :type items: list of items
        """
        self.app.add_items(self.task_id, items)

    def delete(self):
        """
        Delete this task. This object must not be used after calling this method.
        """
        self.app.delete_task(self.task_id)

    def _register_with_server(self):
        params = {
            "app_id": self.app.app_id,
            "description": self.description,
            "humans_per_item": self.humans_per_item,
            "hidden": int(self.hidden),
            "camera": int(self.camera),
            "auto_repeat": int(bool(self.auto_repeat)),
            "human_can_do_multiple": int(bool(self.human_can_do_multiple)),
        }

        if self.latitude is not None:
            params["latitude"] = self.latitude
        if self.longitude is not None:
            params["longitude"] = self.longitude
        if self.radius_miles is not None:
            params["radius_miles"] = self.radius_miles

        if self.items is not None:
            params["items"] = json.dumps(self.items)
        if self.task_id is not None:
            params["task_id"] = str(self.task_id)

        if self.thumbnail:
            params["thumbnail"] = self.thumbnail

        http_response = self.app._call_api("task", params)
        if http_response["status_code"] == 200:
            response = json.loads(http_response["text"])
            self.task_id = response["task_id"]
            self.url = response["url"]
            self.task_hashed_id = response["task_hashed_id"]
        else:
            print "Got %s from server when registering the task" % \
                http_response["status_code"]

    def _human_connected(self, session_id, item, human):
        session = Session(self, session_id, human)
        session.begin_batch()
        self.on_connect_fn(session, self, item)
        session.end_batch()

    def _human_disconnected(self, session_id, human):
        if self.on_disconnect_fn:
            session = Session(self, session_id, human)
            session.begin_batch()
            self.on_disconnect_fn(session, self)
            session.end_batch()

    def _human_submitted(self, session_id, values, human):
        on_submit_fn = None

        if self.on_submit_fns:
            form_name = values.get(FORM_NAME_KEY)
            if form_name:
                on_submit_fn = self.on_submit_fns.get(form_name)
                if not on_submit_fn:
                    print "Warning: Form \"%s\" does not have a submit function." % form_name

        on_submit_fn = on_submit_fn or self.on_submit_fn

        if on_submit_fn:
            session = Session(self, session_id, human)
            session.begin_batch()
            on_submit_fn(session, self, values)
            session.end_batch()


class Session(object):
    """
    Represents a connection to one human. A ``Session`` object is dynamically created
    for each callback. It contains the information the app needs to communicate with
    a human or get information about the human.

    Member variables:

    * human_id: The human ID, a text string that includes letter, numbers, hyphens, and underscores.
    * latitude: Latitude of human.  This may be None, if geolocation is disabled or could not be determined.
    * longitude: Longitude of human.  This may be None, if geolocation is disabled or could not be determined.
    * camera: True if the client app has a camera.
    """

    def __init__(self, task, session_id, human):
        self.task = task
        self.session_id = session_id
        self.batch_level = 0
        self.batched_calls = []

        for key in human:
            assert key not in self.__dict__
            setattr(self, key, human[key])

    def begin_batch(self):
        """
        Begin batch mode, where fields and other user interface elements are
        batched up instead of being sent one by one. When ``end_batch()`` is called,
        all batched elements are sent at once. This provides a better experience
        for users because all elements appear at once. Batching is automatically
        turned on for the connected, disconnected, and submitted callbacks. It
        is harmless to nest begin/end calls.
        """

        self.batch_level += 1

    def end_batch(self):
        """
        End batch mode. Flushes all batched commands. See fuller documentation
        at the ``begin_batch()`` method.
        """

        if self.batch_level > 0:
            self.batch_level -= 1
            self._flush_batch()

    def _call(self, info):
        if not self.task.app.app_id:
            raise Exception("App not connected")

        self.batched_calls.append(info)
        if self.batch_level == 0:
            self._flush_batch()

    def _flush_batch(self):
        if self.batched_calls:
            json_info = json.dumps(self.batched_calls)

            self.task.app._call_api("session/%s/call" % self.session_id,
                                    {"calls": json_info})
            self.batched_calls = []

    def clear_screen(self):
        """
        Clear the screen on the user's UI.
        """
        self._call({"method": "clear_screen"})

    def add_hidden_field(self, name, value):
        """
        Add a hidden input field on the user's page.  Use this to store data that will
        be passed back to your app on the user's next form submit.

        :param name: Name of this input element.  This name will be one of the keys in the key:value pairs returned to your app when someone clicks a submit button in your app.
        :type name: string

        :param value:
        """
        self._call({"method": "add_hidden_field",
                    "name": name,
                    "value": value})

    def set_form_name(self, form_name):
        """
        Sets the name of the current form. Use this to control which
        of your callback handlers will be dispatched when the user
        presses a submit button. See the ``on_submit_fns`` parameter of ``create_task()``.

        :param form_name: The name of the form. It will be looked up in the ``on_submit_fns``
            dictionary.
        :type form_name: string
        """
        self.add_hidden_field(FORM_NAME_KEY, form_name)

    def add_text(self, text, boxed=False):
        """
        Add a line of static text to the user's UI.

        :param text: The text to display to the user. It will be word-wrapped if it exceeds
            the width of the display.
        :type text: string
        :param boxed: Whether to display the text with a decorative box around it. This is
            useful when displaying third-party text, such as a quote, that is not part
            of the form instructions. Defaults to False.
        :type boxed: bool
        """
        self._call({"method": "add_text",
                    "text": text,
                    "boxed": boxed})

    def add_title(self, text):
        """
        Add a line of static bold text to the user's UI.

        :param text: The text to display to the user. It will be word-wrapped if it exceeds
            the width of the display.
        :type text: string
        """
        self._call({"method": "add_title",
                    "text": text})

    def add_submit_button(self, text="", value="", on_submit=""):
        """
        Add a Submit button to the user's UI.  You can add multiple submit buttons.
        Whichever one is pressed, that button's ``value`` will be passed back to your app
        in the ``submit_button`` data field.

        :param text: The text to display within the button.
        :type text: string
        :param value: The value to give the ``submit_button`` form field if this button
            is used to submit the form.
        :type value: string
        :param on_submit: A string indicating the callback function to trigger, from the on_submit_fns dictionary.
        :type on_submit: string
        """

        if not isinstance(on_submit, basestring):
            raise TypeError("on_submit must be a string")

        # The actual default text and value are handled in the client.
        self._call({"method": "add_submit_button",
                    "text": text,
                    "value": value,
                    "on_submit": on_submit})

    def add_image_submit_button(self, url, value, decorated=True, on_submit=""):
        """
        Add a submit button with an image. You can add multiple submit buttons.
        Whichever one is pressed, that button's ``value`` will be passed back to your app
        in the ``submit_button`` data field.

        :param url: URL pointing to an image to display in the submit button.
        :type url: string
        :param value: The value to give the ``submit_button`` form field if this button
            is used to submit the form.
        :type value: string
        :param decorated: If False, the button is just the image. If True (the default),
            the image is wrapped in a button frame.
        :type decorated: bool
        :param on_submit: A string indicating the callback function to trigger, from the on_submit_fns dictionary.
        :type on_submit: string
        """
        if not isinstance(on_submit, basestring):
            raise TypeError("on_submit must be a string")

        self._call({"method": "add_image_submit_button",
                    "url": url,
                    "decorated": decorated,
                    "value": value,
                    "on_submit": on_submit})

    def add_image(self, url, decorated=True):
        """
        Add a passive image to the form.

        :param url: URL pointing to the image to display.
        :type url: string
        :type decorated: If False, the image has no border. If True (the default),
            the image is wrapped in a frame.
        """
        self._call({"method": "add_image",
                    "decorated": decorated,
                    "url": url})

    def add_radio_button(self, name, value, text):
        """
        Add a radio button to the form. For a given ``name``, only one radio button may
        be selected.

        :param name: Name of this input element.  This name will be one of the keys in the key:value pairs returned to your app when someone clicks a submit button in your app. Several radio buttons should share the same name.
        :type name: string
        :param value: The value to associate with the ``name`` in the form values. It specifies
            which radio button was selected when the form was submitted.
        :type value: string
        :param text: The text to display next to the radio button.
        :type text: string
        """
        self._call({"method": "add_radio_button",
                    "name": name,
                    "value": value,
                    "text": text})

    def add_checkbox(self, name, text, default_value=False):
        """
        Add a check box widget to the form.

        :param name: Name of this input element.  This name will be one of the keys in the key:value pairs returned to your app when someone clicks a submit button in your app.
        :type name: string
        :param text: The text to display next to the check box.
        :type text: string
        :param default_value: The value to initially populate the text field with. This is normally an empty string, but can be non-empty if there's a sensible default that many users will want.
        :type default_value: bool
        """
        self._call({"method": "add_checkbox",
                    "name": name,
                    "text": text,
                    "default_value": default_value})

    def add_list_button(self, name, value, text, subtitle=None, on_submit=""):
        """
        Add a list button to the form.

        :param name: Name of this input element.  This name will be one of the keys in the key:value pairs returned to your app when someone clicks a submit button in your app. Several list buttons should share the same name.
        :type name: string
        :param value: The value to associate with the ``name`` in the form values. It specifies
            which list button caused the form to be submitted.
        :type value: string
        :param text: The text to display next to the list button.
        :type text: string
        :param on_submit: A string indicating the callback function to trigger, from the on_submit_fns dictionary.
        :type on_submit: string
        """
        if not isinstance(on_submit, basestring):
            raise TypeError("on_submit must be a string")

        self._call({"method": "add_list_button",
                    "name": name,
                    "value": value,
                    "text": text,
                    "subtitle": subtitle,
                    "on_submit": on_submit})

    def add_camera_button(self, name, quality=49):
        """
        Add a button to take a photo with the device's camera. If the human takes a photo,
        it will be uploaded to the Human.io's file service and the submitted form
        data will contain a URL to the photo.

        :param name: Name of this input element.  This name will be one of the keys in the key:value pairs returned to your app when someone clicks a submit button in your app.
        :type name: string
        :param quality: An int from 1 to 100 indicating the quality of the image.  Note that higher quality will result in a larger image which takes longer to upload from mobile device.  Default is 49.
        :type quality: int
        """
        self._call({"method": "add_camera_button",
                    "quality": quality,
                    "name": name})

    def add_rating_selector(self, name, number_of_stars=0):
        """
        Adds a rating selector to the form. The form will show five stars, of which
        ``number_of_stars`` will be pre-selected. The user can tap one of the stars
        to rate an item. The form results will contain the number of stars selected,
        as an integer.

        :param name: Name of this input element.  This name will be one of the keys in the key:value pairs returned to your app when someone clicks a submit button in your app.
        :type name: string
        :param number_of_stars: The number of stars to initially show selected, or 0
            (the default) to show no stars selected.
        :type number_of_stars: int
        """
        self._call({"method": "add_rating_selector",
                    "name": name,
                    "number_of_stars": number_of_stars})

    def add_link(self, href, text=""):
        """
        Add a link to the form. If the user taps the link, they are taken to a web browser
        to show the contents of the linked page.

        :param href: The URL of the link.
        :type href: string
        :param text: The text of the link.
        :type text: string
        """
        self._call({"method": "add_link",
                    "href": href,
                    "text": text})

    def add_text_field(self, name, keyboard_type="text", default_value=""):
        """
        Add a one-line text field to the form.

        :param name: Name of this input element.  This name will be one of the keys in the key:value pairs returned to your app when someone clicks a submit button in your app.
        :type name: string
        :param keyboard_type: The type of keyboard to show when the text field is selected. This is only a hint; the device is not required to show a special keyboard, and the input field is not restricted to characters from any particular set. The value can be "text" (the default), "email", "number", "tel" (telephone number), and "url".
        :type keyboard_type: string
        :param default_value: The value to initially populate the text field with. This is normally an empty string, but can be non-empty if there's a sensible default that many users will want.
        :type default_value: string
        """
        self._call({"method": "add_text_field",
                    "name": name,
                    "keyboard_type": keyboard_type,
                    "default_value": str(default_value)})

    def add_text_area(self, name):
        """
        Add a multi-line text field to the form.

        :param name: Name of this input element.  This name will be one of the keys in the key:value pairs returned to your app when someone clicks a submit button in your app.
        :type name: string
        """
        self._call({"method": "add_text_area",
                    "name": name})

    def add_map(self, center_latitude, center_longitude, zoom=14, show_marker=False):
        """
        Add a Google map, optionally showing a marker at the center point.

        :param center_latitude: Latitude for map center.
        :type center_latitude: float

        :param center_longitude: Longitude for map center.
        :type center_longitude: float

        :param zoom: Zoom.  Higher values are closer.  A street closeup is usually zoom 17 or 18.
        :type zoom: int

        :param show_marker: Show a placemark at the map center.
        :type show_marker: bool
        """
        self._call({"method": "add_map",
                    "center_latitude": center_latitude,
                    "center_longitude": center_longitude,
                    "zoom": zoom,
                    "show_marker": show_marker})

    def clear_input(self, name):
        # Don't document.
        self._call({"method": "clear_input",
                    "name": name})

    def dismiss(self, approve, delay_seconds=None, new_task_hashed_id=None):
        """
        Dismiss a human and stop the currently-running task.  Optionally provide a new hashed task id to start after dismissing the person from the current task.  This new Task can be from any developer, not just yourself, given you have the hashed task id.

        :param approve: Whether to approve the work that the human has done. If the work
            is not approved, another human can later perform the same work (e.g., receive the
            same data item).
        :type approve: bool
        :param delay_seconds: The optional number of seconds to wait before returning the user to the main menu. This is useful after displaying the last "Thank you" screen. If omitted, dismisses the user immediately.
        :type delay_seconds: float

        :param new_task_hashed_id: The task_hashed_id for another task, as returned when that task was created.  Specify this to send human to a new task after they're dismissed.
        """

        # Flush in case we're batching.
        self._flush_batch()

        params = {
            # task_id and app_id are no longer used by the server. Leaving this here for
            # few releases in case someone uses a new library with an old server.
            "task_id": self.task.task_id,
            "approve": int(approve),
            "app_id": self.task.app.app_id,
        }
        if delay_seconds is not None:
            params["delay_seconds"] = delay_seconds
        if new_task_hashed_id is not None:
            params["new_task_hashed_id"] = new_task_hashed_id

        self.task.app._call_api("session/%s/dismiss" % self.session_id,
                                params)

