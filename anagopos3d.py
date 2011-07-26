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

from lambda_terms.lambda_parser import LambdaParseException
from trs_terms.trs_parser import TRSParseException
from ubigraph import Ubigraph

import operations as operation

TERM_PARSE_ERROR_COLOUR = "#BB4444"

ANAGAPOS = "Anagapos 3D"
VERSION  = "Version 1.0"
URL      = "https://github.com/jeroenk/lambda"

RULE_SET_TEXT  = "Rule set: "
BETA_REDUCTION = "β-rule"

DISP_TERMS_TEXT = "Displayed terms: "
DISP_STEPS_TEXT = "Displayed steps: "

class State:
    def __init__(self):
        self.rule_dir = osenviron["HOME"]

        self.trs_contents    = ""
        self.lambda_contents = ""

        self.ubi = Ubigraph()
        self.reset_terms()

    def set_vertex_style(self):
        self.vertex = self.ubi.newVertexStyle(shape = "sphere",
                                                  color = "#ff0000",
                                                  size = "1.0")

    def set_edge_style(self):
        self.edge = self.ubi.newEdgeStyle(width = "2.0", color = "#ffffff")

    def reset_terms(self):
        self.iterator     = None
        self.terms        = {}
        self.term_count   = 0
        self.cur_term     = 0
        self.reducts      = []
        self.reduct_count = 0
        self.cur_reduct   = 0

        self.ubi.clear()
        self.set_vertex_style()
        self.set_edge_style()

class MainWindow(wx.Frame):

    def __init__(self, parent = None, id = -1, title = ANAGAPOS):
        style = wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX

        wx.Frame.__init__(self, parent, id, title, size = (220, 420),
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
        self.term_input.Bind(wx.EVT_TEXT, self.ResetTextColor)

        # Buttons
        draw_button     = wx.Button(self, 0, "Reset Graph", size = button_size)
        random_button   = wx.Button(self, 0, "Random Term", size = button_size)
        forward_button  = wx.Button(self, 0, "Forward", size = step_size)
        backward_button = wx.Button(self, 0, "Backward", size = step_size)

        self.start_checkbox = wx.CheckBox(self, -1, "Color initial term")
        self.new_checkbox   = wx.CheckBox(self, -1, "Color latest term")


        # Spinners (for choosing step size)
        self.forward_spinner = wx.SpinCtrl(self, -1, "1", min = 1, max = 999,
                                               initial = 1, size = spinner_size)
        forward_box = wx.BoxSizer(wx.HORIZONTAL)
        forward_box.Add(forward_button, 0,
                            wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 10)
        forward_box.Add(self.forward_spinner, 0,
                            wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        self.backward_spinner = wx.SpinCtrl(self, -1, "1", min = 1, max = 999,
                                               initial = 1, size = spinner_size)
        backward_box = wx.BoxSizer(wx.HORIZONTAL)
        backward_box.Add(backward_button, 0,
                            wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 10)
        backward_box.Add(self.backward_spinner, 0,
                            wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)

        # Button/spinner actions
        draw_button.Bind(wx.EVT_BUTTON, self.ResetGraph)
        random_button.Bind(wx.EVT_BUTTON, self.Generate)
        forward_button.Bind(wx.EVT_BUTTON, self.Forward)
        backward_button.Bind(wx.EVT_BUTTON, self.Backward)
        self.start_checkbox.Bind(wx.EVT_CHECKBOX, self.StartCheck)
        self.new_checkbox.Bind(wx.EVT_CHECKBOX, self.NewCheck)

        # Status information
        self.disp_terms = wx.StaticText(self, -1, DISP_TERMS_TEXT + "-")
        self.disp_steps = wx.StaticText(self, -1, DISP_STEPS_TEXT + "-")

        # Layout the control panel
        bts = wx.BoxSizer(wx.VERTICAL)
        bts.Add(radio_box, 0, wx.ALIGN_LEFT | wx.ALL, 10)
        bts.Add(self.active_rule_file_text, 0, wx.ALIGN_LEFT | wx.LEFT, 10)
        bts.Add(self.term_input, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        bts.Add(random_button, 0, wx.ALIGN_CENTER | wx.LEFT | wx.BOTTOM, 3)
        bts.Add(draw_button, 0, wx.ALIGN_CENTER | wx.LEFT | wx.BOTTOM, 3)
        bts.Add(forward_box, 0, wx.ALIGN_CENTER | wx.LEFT | wx.BOTTOM, 3)
        bts.Add(backward_box, 0, wx.ALIGN_CENTER | wx.LEFT | wx.BOTTOM, 3)
        bts.Add(self.start_checkbox, 0, wx.ALIGN_LEFT | wx.LEFT, 10)
        bts.Add(self.new_checkbox, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 10)
        bts.Add(self.disp_terms, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 10)
        bts.Add(self.disp_steps, 0, wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 10)

        # Layout the whole window frame
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(bts, 0, wx.ALIGN_TOP, 15)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

        self.CreateStatusBar()

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

    def LoadRuleSet(self):
        dlg = wx.FileDialog(self, "Open rule set", self.state.rule_dir, "",
                                "TRS files (*.xml)|*.xml", wx.OPEN)

        self.rule_set  = None
        self.rule_name = None

        if dlg.ShowModal() == wx.ID_OK:
            name     = dlg.GetPath()
            rulename = dlg.GetFilename()[:-4]
            suffix   = name[-3:]
            if suffix != 'xml':
                self.SetStatusText("Unrecognized file format: " + suffix)
                return

            self.state.rule_dir = name[:name.index(rulename) - 1]

            operation.set_mode("trs")

            try:
                self.rule_set = operation.parse_rule_set(name)
                self.SetStatusText("Rule set loaded")
            except TRSParseException as exception:
                self.SetStatusText(str(exception))
                return

            self.rule_name = rulename

    def SetRadioVal(self, event):
        self.state.reset_terms()

        if operation.get_mode() == "trs":
            self.state.trs_contents = self.term_input.GetValue()
        elif operation.get_mode() == "lambda":
            self.state.lambda_contents = self.term_input.GetValue()

        if self.radio_lambda.GetValue():
            self.rule_set = None
            self.UpdateRuleInfo(BETA_REDUCTION)
            operation.set_mode("lambda")
            self.term_input.SetValue(self.state.lambda_contents)
        elif self.radio_trs.GetValue():
            self.LoadRuleSet()

            if self.rule_set == None:
                self.radio_lambda.SetValue(True)
                self.UpdateRuleInfo(BETA_REDUCTION)
                operation.set_mode("lambda")
                self.term_input.SetValue(self.state.lambda_contents)
            else:
                self.UpdateRuleInfo(self.rule_name)
                # mode already set by LoadRuleSet
                self.term_input.SetValue(self.state.trs_contents)

    def UpdateRuleInfo(self, text):
        self.active_rule_file_text.SetLabel(RULE_SET_TEXT + text)

    def OnExit(self, event):
        self.Close(True)

    def ResetTextColor(self, event):
        self.term_input.SetBackgroundColour("#FFFFFF")

    def ColorInitial(self):
        latest  = self.state.cur_term == 0 and self.new_checkbox.GetValue()
        initial = self.start_checkbox.GetValue()

        if initial and latest:
            self.state.terms[0].set(color = "#00ffff")
        elif initial:
            self.state.terms[0].set(color = "#0000ff")
        elif latest:
            self.state.terms[0].set(color = "#00ff00")
        else:
            self.state.terms[0].set(color = "#ff0000")

    def ColorLatest(self):
        latest  = self.new_checkbox.GetValue()
        initial = self.state.cur_term == 0 and self.start_checkbox.GetValue()

        if initial and latest:
            self.state.terms[self.state.cur_term].set(color = "#00ffff")
        elif initial:
            self.state.terms[self.state.cur_term].set(color = "#0000ff")
        elif latest:
            self.state.terms[self.state.cur_term].set(color = "#00ff00")
        else:
            self.state.terms[self.state.cur_term].set(color = "#ff0000")

    def ResetGraph(self, event):
        self.state.reset_terms()
        term_string = self.term_input.GetValue()

        try:
            term = operation.parse(term_string)
        except (LambdaParseException) as exception:
            # The parser throws an exception when it fails.
            self.term_input.SetBackgroundColour(TERM_PARSE_ERROR_COLOUR)
            self.SetStatusText(str(exception))
            return

        self.SetStatusText("Parsing successful")

        self.state.iterator = term.__iter__()
        (term, number, previous) = self.state.iterator.next()
        vertex = self.state.ubi.newVertex(style = self.state.vertex)
        self.state.terms[number] = vertex
        self.state.term_count = 1
        self.ColorInitial()
        self.disp_terms.SetLabel(DISP_TERMS_TEXT + str(self.state.cur_term + 1))
        self.disp_steps.SetLabel(DISP_STEPS_TEXT + str(self.state.cur_reduct))
        return

    def GetReduct(self):
        cur_reduct = self.state.cur_reduct

        if cur_reduct < self.state.reduct_count:
            (number, previous, new_dst, _) = self.state.reducts[cur_reduct]
            new_reduct = False
        else:
            (_, number, previous, new_dst) = self.state.iterator.next()
            new_reduct = True

            if new_dst:
                self.state.term_count += 1

            self.state.reduct_count += 1

        if new_dst:
            vertex = self.state.ubi.newVertex(style = self.state.vertex)
            self.state.terms[number] = vertex
            self.state.cur_term += 1

        self.state.cur_reduct += 1
        return (new_reduct, number, previous, new_dst)

    def Forward(self, event):
        self.SetStatusText("")
        reduct_count = self.forward_spinner.GetValue()
        count = reduct_count

        if self.state.iterator == None:
            self.ResetGraph(None)
            reduct_count -= 1

            if self.state.iterator == None or reduct_count == 0:
                return

        try:
            while reduct_count != 0:
                (new_reduct, number, previous, new_dst) = self.GetReduct()

                if new_dst:
                    if number - 1 == 0:
                        self.ColorInitial()
                    else:
                        self.state.terms[number - 1].set(color = "#ff0000")

                    self.ColorLatest()

                if (number != previous):
                    s = self.state.terms[previous]
                    t = self.state.terms[number]
                    edge = self.state.ubi.newEdge(s, t, style = self.state.edge)
                else:
                    edge = None

                reduct = (number, previous, new_dst, edge)
                if new_reduct:
                    self.state.reducts.append(reduct)
                else:
                    self.state.reducts[self.state.cur_reduct - 1] = reduct

                reduct_count -= 1
                self.disp_terms.SetLabel(DISP_TERMS_TEXT \
                                             + str(self.state.cur_term + 1))
                self.disp_steps.SetLabel(DISP_STEPS_TEXT \
                                             + str(self.state.cur_reduct))

            if count == 1:
                self.SetStatusText("Added 1 step")
            else:
                self.SetStatusText("Added " + str(count) + " steps")
        except StopIteration:
            self.SetStatusText("Graph complete")

    def Backward(self, event):
        self.SetStatusText("")
        if self.state.iterator == None:
            self.ResetGraph(None)
            return

        reduct_count = self.backward_spinner.GetValue()
        reduct_count = min(self.state.cur_reduct, reduct_count)
        count = reduct_count

        while reduct_count > 0:
            self.state.cur_reduct -= 1
            (number, previous, new, edge) \
                = self.state.reducts[self.state.cur_reduct]

            if edge != None:
                edge.destroy()

            reduct = (number, previous, new, None)
            self.state.reducts[self.state.cur_reduct] = reduct

            if self.state.reducts[self.state.cur_reduct][2]:
                number = self.state.reducts[self.state.cur_reduct][0]
                self.state.terms[number].destroy()
                self.state.terms[number] = None
                self.state.cur_term -= 1
                self.ColorLatest()

            reduct_count -= 1
            self.disp_terms.SetLabel(DISP_TERMS_TEXT \
                                         + str(self.state.cur_term + 1))
            self.disp_steps.SetLabel(DISP_STEPS_TEXT \
                                         + str(self.state.cur_reduct))


        if count == 1:
            self.SetStatusText("Removed 1 step")
        else:
            self.SetStatusText("Removed " + str(count) + " steps")


    def StartCheck(self, event):
        if self.state.iterator == None:
            self.ResetGraph(None)

            if self.state.iterator == None:
                return

        self.ColorInitial()

    def NewCheck(self, event):
        if self.state.iterator == None:
            self.StartCheck(None)
            return

        self.ColorLatest()


    def Generate(self, event):
        term_string = operation.random_term()
        self.term_input.SetValue(term_string)

app   = wx.PySimpleApp()
frame = MainWindow()

frame.Show(True)
app.MainLoop()

del frame
del app
