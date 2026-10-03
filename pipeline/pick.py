"""Pick the next episode to produce: first episodes/*.json whose current version has no release yet
and no pending feedback. Invalid scripts get their errors filed as feedback for the writer bot."""
import glob, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from check import validate

sh = lambda *a: subprocess.run(a, capture_output=True, text=True, check=True).stdout
released = {r['tagName'] for r in json.loads(sh('gh', 'release', 'list', '--limit', '500', '--json', 'tagName'))}
busy = {i['title'][1:6] for label in ('failed', 'rendering')  # failed: wait for a human/doctor; rendering: another run has it
        for i in json.loads(sh('gh', 'issue', 'list', '--label', label, '--state', 'open', '--json', 'title'))}
out = open(os.environ.get('GITHUB_OUTPUT', os.devnull), 'a')
for f in sorted(glob.glob('episodes/ep*.json')):
    ep = json.load(open(f, encoding='utf-8'))
    tag = f"{ep.get('id')}-v{ep.get('version')}"
    if tag in released or ep.get('id') in busy or os.path.exists(f"feedback/{ep.get('id')}.md"): continue
    errs = validate(ep)
    if errs:
        os.makedirs('feedback', exist_ok=True)
        open(f"feedback/{ep['id']}.md", 'w').write('The pipeline rejected this script. Fix these and bump version:\n- ' + '\n- '.join(errs) + '\n')
        print(f'{f}: invalid, filed feedback'); continue
    print(f'next: {f} ({tag})')
    out.write(f"ep={f}\nid={ep['id']}\ntag={tag}\ntitle={ep['title']}\n")
    break
