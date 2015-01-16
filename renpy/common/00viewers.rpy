# Copyright 2004-2014 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

init -1600 python:
    ##########################################################################
    # DyanmicVariableViewer

    def _dynamic_watch():
        if not config.developer:
            return
        renpy.show_screen("_dynamic_watcher")
        renpy.restart_interaction()

    def _watching_exp(expression):
        return DynamicDisplayable(_dynamic_text, expression=expression)
    def _dynamic_text(st, at, expression):
        try:
            # remove text tags
            return Text(unicode(renpy.python.py_eval(expression)).replace('{', '{{'), substitute=False), .1
        except:
            return Text("Exception"), .1

    if persistent._watch_list is None:
        persistent._watch_list = []

screen _dynamic_watcher:
    zorder 2000

    frame:
        style_group "dynamic_watcher"
        has vbox
        viewport:
            scrollbars "both"
            mousewheel True
            vbox:
                spacing 5
                for i in persistent._watch_list:
                    hbox:
                        textbutton _("x") action [Function(persistent._watch_list.remove, i), Show("_dynamic_watcher")]
                        textbutton "[i!q]" action Function(renpy.call_in_new_context, "_watch_list_add", default=i)
                    hbox:
                        text "    -> " yalign .5
                        text _watching_exp(i) yalign .5
        hbox:
            xalign 1.
            textbutton _("add")   action Function(renpy.call_in_new_context, "_watch_list_add")
            textbutton _("close") action [Function(renpy.hide_screen, "_dynamic_watcher"), renpy.restart_interaction]

init -1600:
        style dynamic_watcher_frame xalign 1.0
        style dynamic_watcher_frame background "#0006"
        style dynamic_watcher_frame xmaximum 600
        style dynamic_watcher_frame ymaximum 300

label _watch_list_add(default=""):
    python:
        v = renpy.call_screen('_input_screen', message=_("Enter adding expression"), default=default)
        if v:
            if default:
                persistent._watch_list.remove(default)
            persistent._watch_list.append(v)
    return

screen _input_screen(message="", default=""):
    modal True
    zorder 100
    key "game_menu" action Return("")

    frame:
        style_group "input_screen"

        has vbox

        label message

        hbox:
            input default default
