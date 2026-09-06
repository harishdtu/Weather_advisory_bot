from app.graph.langgraph_graph import build_graph
import inspect

g = build_graph()
print('compiled type:', type(g))
for name in ['invoke','ainvoke','invoke_stream','run','__call__']:
    print(name, hasattr(g, name))

for name in dir(g):
    if name in ('invoke','ainvoke','invoke_stream'):
        print('\n', name, inspect.signature(getattr(g,name)))
        print('\n doc:', inspect.getdoc(getattr(g,name)))
