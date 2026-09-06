import importlib, inspect
m = importlib.import_module('langgraph')
print('module repr:', repr(m))
print('__file__ attr:', getattr(m, '__file__', None))
print('__spec__ origin:', getattr(m.__spec__, 'origin', None))
from langgraph.graph import StateGraph, START, END
print('StateGraph:', StateGraph)
print('START:', START)
print('END:', END)
print('StateGraph defined in:', inspect.getfile(StateGraph))
