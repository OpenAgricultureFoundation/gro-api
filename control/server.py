#!/usr/bin/env python3
"""
This server is used to control a Django server deployed through uWSGI. It can
send commands to the uWSGI server through it's Master FIFO, allowing the Django
server to effectively restart itself and manage it's deployment configuration by
querying this server. It can also run management commands on the Django server,
allowing it to do things like making and applying migrations by querying this
server.

The HMTL interface for this server uses Bootstrap and jQuery, so these two
libraries must be installed in the :attr:`STATIC_ROOT` folder (as defined in the
settings file for the Django server being controlled) for the HTML pages to
render correctly

This server reads from the following environment variables:

.. envvar:: DJANGO_SETTINGS_MODULE
    The settings file of the Django server being controlled. The file must
    define the variables :attr:`STATIC_ROOT`, the folder in which static files
    for the project are stored, and :attr:`BASE_DIR`, the root directory of the
    Django project for the server being controlled

.. envvar:: CITYFARM_API_MASTER_FIFO
    The uWSGI Master FIFO for the Django server being controlled.

Both of these variables are defined in the :obj:`.env` file generated by
:program:`setup_environment.sh`.
"""

###################
# Imports & Setup #
###################

import os
import importlib
from slugify import slugify
from flask import Flask, request, Response, jsonify, g
from control.exceptions import InvalidFilePath
from control.commands import OutputItem, Command
from control.routines import Routine
# Constants
HTML_MIMETYPE = 'text/html'
JSON_MIMETYPE = 'application/json'
# Create flask app
django_settings = importlib.import_module(os.environ['DJANGO_SETTINGS_MODULE'])
app = Flask(__name__, static_folder=django_settings.STATIC_ROOT)
# Debugging Support
if os.environ['CITYFARM_API_SERVER_MODE'] == 'development':
    app.debug = True
    from werkzeug import DebuggedApplication
    wsgi_app = DebuggedApplication(app)
else:
    wsgi_app = app
# Error Handling
@app.errorhandler(InvalidFilePath)
def handle_invalid_file_path(error):
    response = Response(error.message)
    response.status_code = 500
    return response

###################
# Command Classes #
###################

def command_index():
    if not hasattr(g, 'command_index'):
        g.command_index = 0
    g.command_index += 1
    return g.command_index

class OutputItemWrapper:
    def __init__(self, output_item):
        if not isinstance(output_item, OutputItem):
            raise TypeError('OutputItemWrapper can only wrap OutputItem instances')
        self.output_item = output_item
    @property
    def is_error(self):
        return self.output_item.is_error
    def to_json(self):
        return self.output_item
    def to_html(self):
        if self.output_item.is_error:
            return '<font color="red">{}</font>'.format(self.output_item)
        else:
            return self.output_item

class CommandWrapper:
    def __init__(self, command):
        if not isinstance(command, Command):
            raise TypeError('CommandWrapper can only wrap Command instances')
        self.command = command
        self.command_index = command_index()
    @property
    def title(self):
        return self.command.title
    @property
    def returncode(self):
        return self.command.returncode
    _html_head = """
<div class="panel" id="panel{index}">
  <div class="panel panel-heading" role="tab">
    <h4 class="panel-title">
      <a data-toggle="collapse" data-parent="#accordion" href="#collapse{index}">
        {title}
      </a>
    </h4>
  </div>
  <div id="collapse{index}" class="panel-collapse collapse" role="tabpanel">
    <div class="panel-body">
<pre class="pre-scrollable">"""
    @property
    def html_head(self):
        return self._html_head.format(index=self.command_index,
                title=self.title)
    _html_tail = """
</pre>
    </div class="panel-body">
  </div>
  <script type="text/javascript">
    $("#panel{index}").addClass("{panel_class}");
  </script>
</div>"""
    @property
    def html_tail(self):
        if hasattr(self, "returncode"):
            if self.returncode == 0:
                panel_class = "panel-success"
            else:
                panel_class = "panel-warning"
        else:
            panel_class = "panel-default"
        return self._html_tail.format(index=self.command_index,
                panel_class=panel_class)
    def run(self):
        return self.command.run()
    def to_json(self):
        log = []
        error = []
        for _item in self.run():
            item = OutputItemWrapper(_item)
            log.append(item)
            if line.is_error:
                error.append(item)
        response = {}
        response['log'] = ''.join(item.to_json() for item in log)
        response['error'] = ''.join(item.to_json() for item in error)
        response['returncode'] = self.returncode
    def to_html(self):
        yield self.html_head
        for _item in self.run():
            item = OutputItemWrapper(_item)
            yield item.to_html()
        yield self.html_tail



class RoutineWrapper:
    html_head = """<html>
  <head>
    <script src="static/jquery/js/jquery.min.js"></script>
    <link rel="stylesheet" href="static/bootstrap/css/bootstrap.min.css">
    <link rel="stylesheet" href="static/bootstrap/css/bootstrap-theme.min.css">
    <script src="static/bootstrap/js/bootstrap.min.js"></script>
  </head>
  <body>
    <div class="container">
      <div class="panel-group" id="accordion" role="tablist">"""
    html_tail = """
      </div>
    </div>
    <script type="text/javascript">
        $("#collapse1").addClass("in");
    </script>
  </body>
</html>"""
    def __init__(self, routine):
        if not isinstance(routine, Routine):
            raise TypeError('RoutineWrapper can only wrap Routing instances')
        self.routine = routine
    @property
    def title(self):
        return self.routine.title
    def to_json(self):
        return [command.to_json() for command in self.commands]
    def to_html(self):
        yield self.html_head
        for command in self.commands:
            for item in command.to_html():
                yield item
        yield self.html_tail
    def to_json_response(self):
        return jsonify(self.to_json())
    def to_html_response(self):
        return Response(self.to_html(), mimetype='text/html')
    def to_response(self):
        self.commands = [CommandWrapper(command) for command in
                self.routine.commands]
        json_match_quality = request.accept_mimetypes[JSON_MIMETYPE]
        html_match_quality = request.accept_mimetypes[HTML_MIMETYPE]
        if json_match_quality > html_match_quality:
            return self.to_json_response()
        else:
            return self.to_html_response()

for routine in Routine.__all__:
    routine = RoutineWrapper(routine)
    url_rule = "/" + slugify(routine.title.lower())
    endpoint = routine.title
    @app.route(url_rule, endpoint=endpoint)
    def route():
        return routine.to_response()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)