"""Validate episode JSON. Usage: python pipeline/check.py episodes/ep001.json  |  --vocab"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from world import CAST, SETTINGS, TIMES, ACTIONS, EMOTIONS, STORY_PROPS, PROP_SPOTS


def validate(ep):
    e = []
    if not re.fullmatch(r'ep\d{3}', str(ep.get('id', ''))): e.append('id must look like ep001')
    if not isinstance(ep.get('version'), int) or ep['version'] < 1: e.append('version must be an int >= 1')
    for k, n in (('title', 90), ('lesson', 200), ('description', 1500), ('thumbnail_text', 22)):
        if not isinstance(ep.get(k), str) or not ep[k].strip() or len(ep[k]) > n: e.append(f'{k}: required, max {n} chars')
    if any(c in ep.get('title', '') for c in '<>'): e.append('title must not contain < or >')
    tags = ep.get('tags', [])
    if not isinstance(tags, list) or len(','.join(tags)) > 400: e.append('tags: list, max 400 chars total')
    scenes = ep.get('scenes', [])
    if not 3 <= len(scenes) <= 12: e.append('need 3-12 scenes')
    words = 0
    for i, s in enumerate(scenes):
        p = f'scene {i}'
        if s.get('setting') not in SETTINGS: e.append(f'{p}: setting must be one of {list(SETTINGS)}')
        if s.get('time', 'day') not in TIMES: e.append(f'{p}: time must be one of {list(TIMES)}')
        if not isinstance(s.get('title'), str) or not s['title'].strip(): e.append(f'{p}: title required (used as chapter name)')
        chars = s.get('characters', [])
        if not chars or any(c not in CAST for c in chars) or len(set(chars)) != len(chars) or len(chars) > 5:
            e.append(f'{p}: characters must be 1-5 unique of {list(CAST)}')
        for pr in s.get('props', []):
            name, _, spot = pr.partition('@')
            if name not in STORY_PROPS or (spot and spot not in PROP_SPOTS): e.append(f'{p}: bad prop "{pr}"')
        if not s.get('lines'): e.append(f'{p}: needs lines')
        for j, l in enumerate(s.get('lines', [])):
            q = f'{p} line {j}'
            if l.get('who') != 'narrator' and l.get('who') not in chars: e.append(f'{q}: who must be narrator or a scene character')
            t = l.get('text', '')
            if not t.strip() or len(t) > 320: e.append(f'{q}: text required, max 320 chars')
            words += len(t.split())
            if l.get('action') and l['action'] not in ACTIONS: e.append(f'{q}: action must be one of {ACTIONS}')
            if l.get('everyone') and l['everyone'] not in ACTIONS: e.append(f'{q}: everyone must be one of {ACTIONS}')
            if l.get('emotion') and l['emotion'] not in EMOTIONS: e.append(f'{q}: emotion must be one of {list(EMOTIONS)}')
    if scenes and not 380 <= words <= 1100: e.append(f'{words} words of dialogue; aim for 450-900 (about 3-6 minutes)')
    ss = ep.get('short_scene', 0)
    if not isinstance(ss, int) or not 0 <= ss < max(len(scenes), 1): e.append('short_scene must be a valid scene index')
    tl = ep.get('thumbnail_line', [0, 0])
    try: scenes[tl[0]]['lines'][tl[1]]
    except Exception: e.append('thumbnail_line must be [scene_index, line_index]')
    return e


if __name__ == '__main__':
    if sys.argv[1:] == ['--vocab']:
        print('characters:', {k: v['about'] for k, v in CAST.items()}, '\nsettings:', list(SETTINGS), '\ntimes:', list(TIMES),
              '\nactions:', ACTIONS, '\nemotions:', list(EMOTIONS), '\nprops:', STORY_PROPS, '\nprop spots (prop@spot):', list(PROP_SPOTS))
        sys.exit()
    bad = 0
    for f in sys.argv[1:]:
        errs = validate(json.load(open(f, encoding='utf-8')))
        print(f, 'OK' if not errs else '\n  ' + '\n  '.join(errs))
        bad += bool(errs)
    sys.exit(bad)
