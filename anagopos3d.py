# -*- coding: utf-8 -*-
# Anagopos 3D: A Reduction Graph Visualizer for Term Rewriting and λ-Calculus
#
# Copyright (C) 2010, 2011 Niels Bjørn Bugge Grathwohl,
#                          Jens Duelund Pallesen,
#                          Jeroen Ketema
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx

from os import environ as osenviron

from lambda_parser import LambdaParseException

import operations as operation

TERM_PARSE_ERROR_COLOUR = "#BB4444"

ANAGAPOS = "Anagapos 3D"
VERSION  = "Version 1.0"
URL      = "https://github.com/jeroenk/lambda"

RULE_SET_TEXT  = "Rule set: "
BETA_REDUCTION = "β-rule"

class State:
    def __init__(self):
        self.rule_dir = osenviron["HOME"]

class MainWindow(wx.Frame):

    def __init__(self, parent = None, id = -1, title = ANAGAPOS):
        style = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX

        wx.Frame.__init__(self, parent, id, title, size = (220, 370),
                              style = style)

        self.state = State()

        # Create the radio buttons to select between lambda calculus and TRS.
        self.radio_lambda = wx.RadioButton(self, -1, 'λ-calculus',
                                               style = wx.RB_GROUP)
        self.radio_trs = wx.RadioButton(self, -1, 'TRS')

        self.Bind(wx.EVT_RADIOBUTTON, self.SetRadioVal,
                      id = self.radio_lambda.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.SetRadioVal,
                      id = self.radio_trs.GetId())

        radio_box = wx.BoxSizer(wx.HORIZONTAL)
        radio_box.Add(self.radio_lambda, 0, wx.ALIGN_LEFT, 10)
        radio_box.Add(self.radio_trs, 0, wx.ALIGN_LEFT | wx.LEFT, 10)

        self.radio_lambda.SetValue(True) # Lambda is by default active
        operation.set_mode("lambda")

        self.radio_lambda.SetToolTip(wx.ToolTip("λβ-calculus"))
        self.radio_trs.SetToolTip(wx.ToolTip("Opens file dialog to select TRS"))

        self.active_rule_file_text \
            = wx.StaticText(self, -1, RULE_SET_TEXT + BETA_REDUCTION)

        # Sizes for the various buttons and text fields
        width         = 200
        spinner_width = 60
        button_size   = (width, -1)
        spinner_size  = (spinner_width, -1)
        step_size     = (width - spinner_width, -1)

        # Term text field
        self.term_input = wx.TextCtrl(self, 0, style = wx.TE_MULTILINE,
                                          size = (width, 100))

        # Buttons
        draw_button     = wx.Button(self, 0, "Draw Graph", size = button_size)
        random_button   = wx.Button(self, 0, "Random Term", size = button_size)
        forward_button  = wx.Button(self, 0, "Forward", size = step_size)
        backward_button = wx.Button(self, 0, "Backward", size = step_size)

        start_checkbox  = wx.CheckBox(self, -1, "Show start")
        newest_checkbox = wx.CheckBox(self, -1, "Show newest")


        # Spinners (for choosing step size)
        self.forward_spinner = wx.SpinCtrl(self, -1, "1", min = 1, max = 100,
                                               initial = 1, size = spinner_size)
        forward_box = wx.BoxSizer(wx.HORIZONTAL)
        forward_box.Add(forward_button, 0,
                            wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 10)
        forward_box.Add(self.forward_spinner, 0,
                            wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        self.backward_spinner = wx.SpinCtrl(self, -1, "1", min = 1, max = 100,
                                               initial = 1, size = spinner_size)
        backward_box = wx.BoxSizer(wx.HORIZONTAL)
        backward_box.Add(backward_button, 0,
                            wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 10)
        backward_box.Add(self.backward_spinner, 0,
                            wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)

        # Button/spinner actions
        draw_button.Bind(wx.EVT_BUTTON, self.DrawGraph)
        random_button.Bind(wx.EVT_BUTTON, self.Generate)
        # XXX forward and backward binds

        # Layout the control panel
        bts = wx.BoxSizer(wx.VERTICAL)
        bts.Add(radio_box, 0, wx.ALIGN_LEFT | wx.ALL, 10)
        bts.Add(self.active_rule_file_text, 0, wx.ALIGN_LEFT | wx.LEFT, 10)
        bts.Add(self.term_input, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        bts.Add(random_button, 0, wx.ALIGN_CENTER | wx.LEFT | wx.BOTTOM, 3)
        bts.Add(draw_button, 0, wx.ALIGN_CENTER | wx.LEFT | wx.BOTTOM, 3)
        bts.Add(forward_box, 0, wx.ALIGN_CENTER | wx.LEFT | wx.BOTTOM, 3)
        bts.Add(backward_box, 0, wx.ALIGN_CENTER | wx.LEFT | wx.BOTTOM, 3)
        bts.Add(start_checkbox, 0, wx.ALIGN_LEFT | wx.LEFT, 10)
        bts.Add(newest_checkbox, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 10)

        # Layout the whole window frame
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(bts, 0, wx.ALIGN_TOP, 15)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

        self.CreateStatusBar()

        # XXX fix status bar
        # self.SetStatusText(s)

        # Menus
        filemenu = wx.Menu()

        # Menu actions
        menuitem = filemenu.Append(-1, "&Open Rule Set\tCtrl+O",
                                                          "Load TRS rule set")
        self.Bind(wx.EVT_MENU, self.OnLoadRuleSet, menuitem)

        filemenu.AppendSeparator()
        menuitem = filemenu.Append(wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuitem)
        menuitem = filemenu.Append(wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnExit, menuitem)

        # Menubar, containg the menu(s) created above
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        self.SetMenuBar(menubar)

        # XXX
        # self.lambda_contents = self.trs_contents = ""

    def OnAbout(self,event):
        message = ANAGAPOS + " " + VERSION + "\n\n"
        message += "URL: " + URL + "\n\n"
        message += "Niels Bjørn Bugge Grathwohl\n"
        message += "Jeroen Ketema\n"
        message += "Jens Duelund Pallesen\n"
        message += "Jakob Grue Simonsen"

        wx.MessageBox(message, "", wx.OK)

    def OnLoadRuleSet(self, event):
        self.radio_trs.SetValue(True)
        self.SetRadioVal(event)

    def loadRuleSet(self):
        dlg = wx.FileDialog(self, "Open rule set", self.state.rule_dir, "",
                                "TRS files (*.xml)|*.xml", wx.OPEN)

        self.rule_set  = None
        self.rule_name = None

        if dlg.ShowModal() == wx.ID_OK:
            name     = dlg.GetPath()
            rulename = dlg.GetFilename()[:-4]
            suffix   = name[-3:]
            if suffix != 'xml':
                print "Unrecognized file format: " + name
                return

            self.state.rule_dir = name[:name.index(rulename) - 1]

            # XXX next line needs to be fixed
            # operations.setmode('trs')

            with open(name, 'r') as f:
                contents = f.read()

            # XXX next line needs to be fixed
            #self.rule_set = operations.parse_rule_set(suffix, contents)
            self.rule_name = rulename

    # XXX
    def SetRadioVal(self, event):
        if self.radio_lambda.GetValue():
            self.rule_set = None
            self.UpdateRuleInfo(BETA_REDUCTION)
            operation.setmode("lambda")
            # self.trs_contents = self.term_input.GetValue()
            # self.term_input.SetValue(self.lambda_contents)
        elif self.radio_trs.GetValue():
            self.loadRuleSet()

            if self.rule_set == None:
                self.radio_lambda.SetValue(True)
                self.UpdateRuleInfo(BETA_REDUCTION)
                operation.set_mode("lambda")
                # self.trs_contents = self.term_input.GetValue()
                # self.term_input.SetValue(self.lambda_contents)
            else:
                self.UpdateRuleInfo(self.rule_name)
                operation.set_mode("trs")
                # self.lambda_contents = self.term_input.GetValue()
                # self.term_input.SetValue(self.trs_contents)

    def UpdateRuleInfo(self, text):
        self.active_rule_file_text.SetLabel(RULE_SET_TEXT + text)

    def OnExit(self,event):
        self.Close(True)

    # XXX
    def DrawGraph(self, drawing):
        term_string = self.term_input.GetValue()

        try:
            term = operation.parse(term_string)
        except (LambdaParseException) as exception:
            # The parser throws an exception when it fails.
            self.term_input.SetBackgroundColour(TERM_PARSE_ERROR_COLOUR)
            self.SetStatusText(exception.__str__())
            return

        self.SetStatusText("Parsing complete")

        return

        self.term_input.SetBackgroundColour("#FFFFFF")
        self.drawing.mgs = []
        operations.assignvariables(self.drawing.term)
        self.drawing.startnumber = 1
        try:
            def iterator():
                Drawer = self.drawing.selected
                for (i,g) in enumerate(operations.reductiongraphiter(self.drawing.term, self.drawing.startnum, self.drawing.endnum, self.rule_set)):
                    yield g
            self.drawing.iterator = iterator()
        except KeyError:
            pass

        rg = self.drawing.iterator.next()
        g = Drawer(rg)
        self.drawing.reductiongraphlist = [rg]
        self.drawing.graph = g
        self.drawing.graphlist = [g]
        self.drawing.graphnumber = 0
        self.drawing.nomoregraphs = False
        self.drawing.starttobig = False

        self.drawing.graph.update_layout_animated(self.drawing.iter_animated)

        # self.drawing.Draw()

    def Generate(self, event):
        term = operation.random_term()
        self.term_input.SetValue(term)

app   = wx.PySimpleApp()
frame = MainWindow()

frame.Show(True)
app.MainLoop()

del frame
del app
