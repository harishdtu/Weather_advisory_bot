from app.graph.nodes import node_parse_user_request, node_match_sops
from app.policies.loader import load_sops
from pprint import pprint

sops = load_sops('policies/sops.yaml')
state = {'raw_input': 'Can I go running today in Bangalore?'}
state = node_parse_user_request(state)
print('Parsed intent:')
print(state['intent'])
# synthetic weather that does not trigger conditions
weather = {'current': {'temperature_2m': 25, 'wind_speed_10m': 5, 'wind_gusts_10m': 0, 'precipitation': 0, 'precipitation_probability': 0, 'uv_index': 5, 'weather_code': 0}}
state['weather'] = weather
# Invoke match sops
state = node_match_sops(state)
print('\nMatch results:')
print('no_policy:', state.get('no_policy'))
print('matched_sops:', state.get('matched_sops'))
print('matched_sops_full:', state.get('matched_sops_full'))
