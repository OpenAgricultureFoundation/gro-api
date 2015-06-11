#!/usr/bin/env python3
"""
This server allows the routines defined in the :mod:`~control.routines` module
to be triggered by a GET request. It generates an endpoint for each routine in
:mod:`~control.routines` that triggers the corresponding routine. Each endpoint
is named based on the title of the routine. This module also reads from the
environment variable :envvar:`CITYFARM_API_SERVER_MODE` to determine whether or
not to run in debug mode.
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
from control.routines import Routine, all_routines
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
    """
    Returns the index of the current command in the current request. Each
    :class:`~control.server.CommandWrapper` instance calls this function upon
    construction so that it knows where it is in the routine.
    """
    if not hasattr(g, 'command_index'):
        g.command_index = 0
    g.command_index += 1
    return g.command_index

class OutputItemWrapper:
    """
    Wraps :class:`~control.commands.OutputItem` to allow it to be rendered as
    HTML or JSON
    """
    def __init__(self, output_item):
        if not isinstance(output_item, OutputItem):
            raise TypeError('OutputItemWrapper can only wrap OutputItem instances')
        self.output_item = output_item
    @property
    def is_error(self):
        """ The :attr:`is_error` attribute of the wrapped item """
        return self.output_item.is_error
    def to_json(self):
        """
        Renders the wrapped :class:`~control.commands.OutputItem` as JSON
        """
        return self.output_item
    def to_html(self):
        """
        Renders the wrapped :class:`~control.commands.OutputItem` as HTML
        """
        if self.output_item.is_error:
            return '<font color="red">{}</font>'.format(self.output_item)
        else:
            return self.output_item

class CommandWrapper:
    """
    Wraps :class:`~control.commands.Command` to allow it to be rendered as HTML
    or JSON
    """
    def __init__(self, command):
        if not isinstance(command, Command):
            raise TypeError('CommandWrapper can only wrap Command instances')
        self.command = command
        self.command_index = command_index()
    @property
    def title(self):
        """ The :attr:`title` attribute of the wrapped command """
        return self.command.title
    @property
    def returncode(self):
        """ The :attr:`returncode` attribute of the wrapped command """
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
        """
        Calls the :func:`~control.commands.Command.run` function of the
        wrapped command
        """
        return self.command.run()
    def to_json(self):
        """
        Renders the result of this command as JSON. The response has the keys
        'log' (the entire log of the command as a string), 'error' (the error
        messages returned by the command), and 'returncode' (the return code of
        the command).
        """
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
        """
        Renders the result of this command as HTML.
        """
        yield self.html_head
        for _item in self.run():
            item = OutputItemWrapper(_item)
            yield item.to_html()
        yield self.html_tail



class RoutineWrapper:
    """
    Wraps :class:`~control.routines.Routing` to allow it to be rendered as HTML
    or JSON
    """
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
            raise TypeError('RoutineWrapper can only wrap Routine instances')
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

for Routine in all_routines:
    url_rule = "/" + slugify(Routine.title.lower())
    endpoint = Routine.title
    @app.route(url_rule, endpoint=endpoint)
    def route():
        return RoutineWrapper(Routine()).to_response()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
