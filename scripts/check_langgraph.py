import importlib, importlib.util
spec = importlib.util.find_spec('langgraph')
print('spec:', spec)
print('origin:', getattr(spec, 'origin', None))
print('submodule_search_locations:', getattr(spec, 'submodule_search_locations', None))
try:
    mod = importlib.import_module('langgraph.graph')
    print('langgraph.graph __file__:', getattr(mod, '__file__', None))
    print('has StateGraph:', hasattr(mod, 'StateGraph'))
    for name in ('StateGraph','START','END'):
        print(name, '->', getattr(mod, name, None))
except Exception as e:
    print('error importing langgraph.graph:', e)
