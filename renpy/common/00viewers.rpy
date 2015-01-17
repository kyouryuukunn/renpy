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
    # TransformViewer
    class TransformViewer(object):
        def __init__(self):

            self.int_range = 1500
            self.float_range = 7.0
            # layer->tag->property->value
            self.state_org = {}
            # {property:(default, float)}, default is used when property can't be got.
            self.props_default = {
            "xpos":(0., False),
            "ypos":(0., False),
            "xanchor":(0., False),
            "yanchor":(0., False),
            "xzoom":(1., True),
            "yzoom":(1., True),
            "zoom":(1., True),
            "rotate":(0, False),
            "alpha":(1., True),
            "additive":(0., True),
            }

        def viewer(self):
            if not config.developer:
                return
            sle = renpy.game.context().scene_lists
            # back up for reset()
            for layer in config.layers:
                self.state_org[layer] = {}
                for tag in sle.layers[layer]:
                    d = sle.get_displayable_by_tag(layer, tag[0])
                    if isinstance(d, renpy.display.screen.ScreenDisplayable):
                        break
                    pos = renpy.get_placement(d)
                    state = getattr(d, "state", None)

                    self.state_org[layer][tag[0]] = {}
                    for p in ["xpos", "ypos", "xanchor", "yanchor"]:
                        self.state_org[layer][tag[0]][p] = getattr(pos, p, None)
                    for p in self.props_default:
                        if not self.state_org[layer][tag[0]].has_key(p):
                            self.state_org[layer][tag[0]][p] = getattr(state, p, None)
            renpy.call_in_new_context("_transform_viewer", viewer=self)

        def reset(self):
            for layer in config.layers:
                for tag, props in self.state_org[layer].iteritems():
                    if tag and props:
                        kwargs = props.copy()
                        for p in self.props_default:
                            if kwargs[p] is None and p != "rotate":
                                kwargs[p] = self.props_default[p][0]
                        renpy.show(tag, [Transform(**kwargs)], layer=layer)
            renpy.restart_interaction()

        def generate_changed(self, layer, tag, prop, int=False):
            def changed(v):
                kwargs = {}
                for p in self.props_default:
                    kwargs[p] = self.get_state(layer, tag, p, False)

                if int and not self.props_default[prop][1]:
                    kwargs[prop] = v - self.int_range
                else:
                    kwargs[prop] = v -self.float_range
                renpy.show(tag, [Transform(**kwargs)], layer=layer)
                renpy.restart_interaction()
            return changed

        def get_state(self, layer, tag, prop, default=True):
            sle = renpy.game.context().scene_lists

            if tag:
                d = sle.get_displayable_by_tag(layer, tag)
                pos = renpy.get_placement(d)
                state = getattr(pos, prop, None)
                if state is None:
                    state = getattr(getattr(d, "state", None), prop, None)
                # set default
                if state is None and default:
                    state = self.props_default[prop][0]
                if state and self.props_default[prop][1]:
                    state = float(state)
                return state
            return None

        def put_clipboard(self, prop, value):
            if renpy.put_clipboard("%s %s" % (prop, value)):
                renpy.notify('Putted "%s %s" on clipboard' % (prop, value))
            else:
                renpy.notify(_("Can't open clipboard"))

        def edit_value(self, function, int=False):
            v = renpy.call_in_new_context("_edit_value")
            if v:
                try:
                    if int:
                        v = renpy.python.py_eval(v) + self.int_range
                    else:
                        v = renpy.python.py_eval(v) + self.float_range
                    function(v)
                except:
                    renpy.notify(_("Please type value"))
    _transform_viewer = TransformViewer()

label _transform_viewer(viewer):
    show screen _transform_viewer(viewer)
    $ui.interact()

    return

screen _transform_viewer(viewer, layer="master", tag=""):
    key "game_menu" action Return()
    zorder 10

    frame:
        xfill True
        style_group "transform_viewer"
        has vbox

        hbox:
            xfill False
            label _("layers")
            for l in config.layers:
                if l not in ["screens", "transient", "overlay"]:
                    textbutton "[l]" action [SelectedIf(l == layer), Show("_transform_viewer", viewer=viewer, layer=l)]
        hbox:
            xfill False
            label _("images")
            for t in viewer.state_org[layer]:
                textbutton "[t]" action [SelectedIf(t == tag), Show("_transform_viewer", viewer=viewer, layer=layer, tag=t)]

        if tag:
            for p in sorted(viewer.props_default.keys()):
                $state = viewer.get_state(layer, tag, p)
                if isinstance(state, int):
                    hbox:
                        $ f = viewer.generate_changed(layer, tag, p, True)
                        textbutton "[p]" action Function(viewer.put_clipboard, p, state)
                        textbutton "[state]" action Function(viewer.edit_value, f, int)
                        bar adjustment ui.adjustment(range=viewer.int_range*2, value=state+viewer.int_range, page=1, changed=f) xalign 1.
                elif isinstance(state, float):
                    hbox:
                        $ f = viewer.generate_changed(layer, tag, p)
                        textbutton "[p]" action Function(viewer.put_clipboard, p, state)
                        textbutton "[state:>.4]" action Function(viewer.edit_value, f)
                        bar adjustment ui.adjustment(range=viewer.float_range*2, value=state+viewer.float_range, page=.05, changed=f) xalign 1.
        hbox:
            xfill False
            xalign 1.
            textbutton _("reset") action [viewer.reset, renpy.restart_interaction]
            textbutton _("close") action Return()

init -1600:
    style transform_viewer_frame background "#0006"
    style transform_viewer_button size_group "transform_viewer"
    style transform_viewer_button_text xalign .5
    style transform_viewer_label xminimum 100
    style transform_viewer_vbox xfill True


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
