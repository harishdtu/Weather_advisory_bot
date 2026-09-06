from app.graph.langgraph_graph import build_graph

compiled = build_graph()
print('compiled type:', type(compiled))
print('has invoke:', hasattr(compiled, 'invoke'))
print('has ainvoke:', hasattr(compiled, 'ainvoke'))
print('has invoke_stream:', hasattr(compiled, 'invoke_stream'))

state = {'session_id': 'sess1', 'raw_input': 'Is it safe to cycle?'}
try:
    if hasattr(compiled, 'invoke'):
        out = compiled.invoke(state)
        print('invoke result:', out)
    elif hasattr(compiled, 'ainvoke'):
        import asyncio
        out = asyncio.get_event_loop().run_until_complete(compiled.ainvoke(state))
        print('ainvoke result:', out)
    else:
        print('No invoke methods found; available attrs:')
        print([a for a in dir(compiled) if not a.startswith('_')])
except Exception as e:
    print('ERROR during invoke:', type(e), e)
