from sublime_db.core.typecheck import TYPE_CHECKING

if TYPE_CHECKING: from .client import DebugAdapterClient

class Thread:
	def __init__(self, id: int, name: str) -> None:
		self.id = id
		self.name = name
		self.stopped = False
		self.selected = False
		self.expanded = False

class StackFramePresentation:
	normal = 1
	label = 2
	subtle = 3

class StackFrame:
	def __init__(self, id: int, file: str, name: str, line: int, internal: bool, presentation: int) -> None:
		self.id = id
		self.name = name
		self.file = file
		self.line = line
		self.internal = internal
		self.presentation = presentation

	@staticmethod
	def from_json(frame: dict) -> 'StackFrame':
		internal = False
		file = '??'
		source = frame.get('source')
		if source:
			path = source.get('path')
			if path: file = path
			else: internal = True		

		hint = frame.get('presentationHint', 'normal')

		if hint == 'label':
			presentation = StackFramePresentation.label
		elif hint == 'subtle':
			presentation = StackFramePresentation.subtle
		else:
			presentation = StackFramePresentation.normal
		
		return StackFrame(
			frame['id'], 
			file, 
			frame['name'], 
			frame.get('line', 0), 
			internal, 
			presentation
		)


class Scope:
	def __init__(self, client: 'DebugAdapterClient', name: str, variablesReference: int, expensive: bool) -> None:
		self.client = client
		self.name = name
		self.variablesReference = variablesReference
		self.expensive = expensive

	@staticmethod
	def from_json(client: 'DebugAdapterClient', json: dict) -> 'Scope':
		return Scope(
			client, 
			json['name'], 
			json['variablesReference'], 
			json['expensive']
		)

class Variable:
	def __init__(self, client: 'DebugAdapterClient', name: str, value: str, variablesReference: int, containerVariablesReference: int = 0) -> None:
		self.client = client
		self.name = name
		self.value = value
		self.containerVariablesReference = 0
		self.variablesReference = variablesReference

	@staticmethod
	def from_json(client: 'DebugAdapterClient', json: dict) -> 'Variable':
		return Variable(
			client, 
			json['name'], 
			json['value'], 
			json.get('variablesReference', 0) 
		)

class EvaluateResponse:
	def __init__(self, result: str, variablesReference: int) -> None:
		self.result = result
		self.variablesReference = variablesReference
		

class CompletionItem:
	def __init__(self, label: str, text: str) -> None:
		self.label = label
		self.text = text

	@staticmethod
	def from_json(json: dict) -> 'CompletionItem':
		return CompletionItem(
			json['label'], 
			json.get('text', None), 
		)
