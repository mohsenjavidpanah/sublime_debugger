from ..typecheck import *
from ..import core, ui, dap

from .debugger_sessions import DebuggerSessions
from .debugger_project import DebuggerProject
from .variables import Variable, VariableComponent

import sublime
import re

# Provides support for showing debug information when an expression is hovered
# sends the hovered word to the debug adapter to evaluate and shows a popup with the result
# word seperates and a word match regex can optionally be defined in the configuration to allow support
# for treating things like $word keeping the $ as part of the word

class ViewHoverProvider(core.Disposables):
	def __init__(self, project: DebuggerProject, sessions: DebuggerSessions) -> None:
		super().__init__()
		self.sessions = sessions
		self.project = project
		self += core.on_view_hovered.add(self.on_hover)

	@core.schedule
	async def on_hover(self, event: Tuple[sublime.View, int, int]):
		(view, point, hover_zone) = event
		if hover_zone != sublime.HOVER_TEXT or not self.project.is_source_file(view):
			return

		session = self.sessions.active

		r = session.adapter_configuration.on_hover_provider(view, point)
		if not r:
			return
		word_string, region = r
		
		try:
			response = await session.adapter.Evaluate(word_string, session.selected_frame, 'hover')
			await core.sleep(0.25)
			variable = dap.Variable("", response.result, response.variablesReference)
			view.add_regions('selected_hover', [region], scope="comment", flags=sublime.DRAW_NO_OUTLINE)

			def on_close() -> None:
				view.erase_regions('selected_hover')

			component = VariableComponent(Variable(session, variable))
			component.toggle_expand()
			ui.Popup(component, view, region.a, on_close=on_close)

		# errors trying to evaluate a hover expression should be ignored
		except dap.Error as e:
			core.log_error("adapter failed hover evaluation", e)
