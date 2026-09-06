import inspect
from importlib import import_module
mod = import_module('langgraph.graph.state')
StateGraph = getattr(mod, 'StateGraph')
print('StateGraph repr:', StateGraph)
print('add_edge signature:', inspect.signature(StateGraph.add_edge))
print('methods:', [m for m in dir(StateGraph) if not m.startswith('_')])
# Print doc of add_edge
print('\nadd_edge doc:\n', inspect.getdoc(StateGraph.add_edge))
