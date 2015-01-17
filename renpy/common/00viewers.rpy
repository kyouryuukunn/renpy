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
    # CameraViewer

    class CameraViewer(object):

        def __init__(self):
            self.range_x         = 5000
            self.range_y         = 5000
            self.range_z         = 10000
            self.range_r         = 360
            self.range_film_size = 300
            self.range_layer_z   = 10000

        def viewer(self):
            if not config.developer:
                return
            self._camera_x = _camera_x
            self._camera_y = _camera_y
            self._camera_z = _camera_z
            self._camera_r = _camera_r
            self._3d_layers = _3d_layers.copy()
            self._film_size = _film_size
            renpy.call_in_new_context("_camera_viewer", viewer=self)

        def camera_reset(self):
            global _film_size
            camera_move(self._camera_x, self._camera_y, self._camera_z, self._camera_r)
            renpy.restart_interaction()
            _film_size = self._film_size

        def layer_reset(self):
            global _3d_layers
            for layer in _3d_layers:
                layer_move(layer, self._3d_layers[layer][2])
            renpy.restart_interaction()

        def x_changed(self, v):
            camera_move(v - self.range_x, _camera_y, _camera_z, _camera_r)
            renpy.restart_interaction()

        def y_changed(self, v):
            camera_move(_camera_x, v - self.range_y, _camera_z, _camera_r)
            renpy.restart_interaction()

        def z_changed(self, v):
            camera_move(_camera_x, _camera_y, v - self.range_z, _camera_r)
            renpy.restart_interaction()

        def r_changed(self, v):
            camera_move(_camera_x, _camera_y, _camera_z, v - self.range_r)
            renpy.restart_interaction()

        # def f_changed(self, v):
        #     set_film_size(v)
        #     renpy.restart_interaction()

        def generate_layer_z_changed(self, l):
            def layer_z_changed(v):
                layer_move(l, v)
                renpy.restart_interaction()
            return layer_z_changed

        def put_clipboard(self, camera_tab, layer=""):
            string = ""
            if camera_tab:
                string = '$camera_move(%s, %s, %s, %s, duration=0)' % (_camera_x, _camera_y, _camera_z, _camera_r)
            else:
                string = '$layer_move("%s", %s)' % (layer, _3d_layers[layer][2])
            if renpy.put_clipboard(string):
                renpy.notify("Putted '%s' on clipboard" % string)
            else:
                renpy.notify(_("Can't open clipboard"))

        def edit_value(self, function, range):
            v = renpy.call_in_new_context("_edit_value")
            if v:
                try:
                    function(renpy.python.py_eval(v) + range)
                except:
                    renpy.notify(_("Please type value"))
    _camera_viewer = CameraViewer()

label _camera_viewer(viewer):
    show screen _camera_viewer(viewer)
    $ui.interact()

    return

screen _camera_viewer(viewer, camera_tab=True):
    key "game_menu" action Return()
    zorder 10

    frame:
        yalign 1.
        style_group "camera_viewer"
        has vbox
        hbox:
            xfill False
            textbutton _("Camera") action [SelectedIf(camera_tab), Show("_camera_viewer", viewer=viewer)]
            textbutton _("3D Layers") action [SelectedIf(not camera_tab), Show("_camera_viewer", viewer=viewer, camera_tab=False)]
        if camera_tab:
            hbox:
                label "x"
                textbutton "[_camera_x]" action Function(viewer.edit_value, viewer.x_changed, viewer.range_x)
                bar adjustment ui.adjustment(range=viewer.range_x*2, value=_camera_x+viewer.range_x, page=1, changed=viewer.x_changed) xalign 1.
            hbox:
                label "y"
                textbutton "[_camera_y]" action Function(viewer.edit_value, viewer.y_changed, viewer.range_y)
                bar adjustment ui.adjustment(range=viewer.range_y*2, value=_camera_y+viewer.range_y, page=1, changed=viewer.y_changed) xalign 1.
            hbox:
                label "z"
                textbutton "[_camera_z]" action Function(viewer.edit_value, viewer.z_changed, viewer.range_z)
                bar adjustment ui.adjustment(range=viewer.range_z*2, value=_camera_z+viewer.range_z, page=1, changed=viewer.z_changed) xalign 1.
            hbox:
                label "rotate"
                textbutton "[_camera_r]" action Function(viewer.edit_value, viewer.r_changed, viewer.range_r)
                bar adjustment ui.adjustment(range=viewer.range_r*2, value=_camera_r+viewer.range_r, page=1, changed=viewer.r_changed) xalign 1.
            # hbox:
            #     label "film size"
            #     textbutton "[_film_size]" action Function(viewer.edit_value, viewer.f_changed, 0)
            #     bar adjustment ui.adjustment(range=viewer.range_film_size, value=_film_size, page=1, changed=viewer.f_changed) xalign 1.
        else:
            for layer in sorted(_3d_layers.keys()):
                hbox:
                    textbutton "[layer]" action Function(viewer.put_clipboard, camera_tab, layer)
                    textbutton "{}".format(int(_3d_layers[layer][2])) action Function(viewer.edit_value, viewer.generate_layer_z_changed(layer), 0)
                    bar adjustment ui.adjustment(range=viewer.range_layer_z, value=_3d_layers[layer][2], page=1, changed=viewer.generate_layer_z_changed(layer)) xalign 1.
        hbox:
            xfill False
            xalign 1.
            if camera_tab:
                textbutton _("clip board") action Function(viewer.put_clipboard, camera_tab)
            textbutton _("reset") action [If(camera_tab, true=viewer.camera_reset, false=viewer.layer_reset), renpy.restart_interaction]
            textbutton _("close") action Return()

init -1600:
    style camera_viewer_frame background "#0006"
    style camera_viewer_label xminimum 100
    style camera_viewer_hbox xfill True
    style camera_viewer_button size_group "camera_viewer"
    style camera_viewer_button_text xalign .5

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

label _edit_value():
    return renpy.call_screen('_input_screen', message=_("Type value"))

init -1600:
    style input_screen_frame xfill True ypos .1 xmargin .05 ymargin .05
    style input_screen_vbox xfill True spacing 30
    style input_screen_label xalign .5
    style input_screen_hbox  xalign .5
