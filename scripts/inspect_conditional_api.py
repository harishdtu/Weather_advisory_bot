import inspect
from importlib import import_module
mod = import_module('langgraph.graph.state')
StateGraph = getattr(mod, 'StateGraph')
print('add_conditional_edges signature:', inspect.signature(StateGraph.add_conditional_edges))
print('\nadd_conditional_edges doc:\n', inspect.getdoc(StateGraph.add_conditional_edges))
print('\nset_conditional_entry_point signature:', inspect.signature(StateGraph.set_conditional_entry_point))
print('\nset_conditional_entry_point doc:\n', inspect.getdoc(StateGraph.set_conditional_entry_point))
print('\nset_entry_point signature:', inspect.signature(StateGraph.set_entry_point))
print('\nset_entry_point doc:\n', inspect.getdoc(StateGraph.set_entry_point))
print('\nset_finish_point signature:', inspect.signature(StateGraph.set_finish_point))
print('\nset_finish_point doc:\n', inspect.getdoc(StateGraph.set_finish_point))
