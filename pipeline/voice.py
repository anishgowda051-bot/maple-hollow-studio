"""Voice bot: Kokoro TTS per line -> dialogue.wav, timeline.json (frames, lip-sync), subs.srt.
Usage: python pipeline/voice.py episodes/ep001.json work/  [--dry  (no TTS: silent timing for local tests)]"""
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from world import CAST, NARRATOR, FPS
from check import validate

SR, HOP = 24000, 24000 // FPS
CHUNK = int(os.environ.get('CHUNK', 240))  # frames per render job
_pipes = {}


def fx(audio, v):
    p = v['pitch']
    chain = f"asetrate={int(SR * p)},aresample={SR},atempo={1 / p:.4f}" + (',' + v['fx'] if v.get('fx') else '')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', chain, '-f', 'f32le', '-'],
                       input=audio.astype('<f4').tobytes(), capture_output=True, check=True)
    return np.frombuffer(r.stdout, '<f4')


def tts(text, who, dry):
    v = NARRATOR if who == 'narrator' else CAST[who]
    if dry: return np.zeros(int(SR * (0.6 + len(text.split()) / 2.6)), 'f4')
    from kokoro import KPipeline
    lang = v['voice'][0]
    if lang not in _pipes: _pipes[lang] = KPipeline(lang_code=lang, repo_id='hexgrad/Kokoro-82M')
    parts = [a.numpy() if hasattr(a, 'numpy') else np.asarray(a) for _, _, a in _pipes[lang](text, voice=v['voice'], speed=v['speed']) if a is not None]
    return fx(np.concatenate(parts).astype('f4'), v)


def srt_time(s):
    ms = int(round(s * 1000)); return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'


def cues(text, t0, t1, width=80):
    """Split long text into <=width-char cues, timed by character share."""
    words, out, cur = text.split(), [], ''
    for w in words:
        if cur and len(cur) + len(w) + 1 > width: out.append(cur); cur = w
        else: cur = f'{cur} {w}'.strip()
    out.append(cur)
    total, t = sum(map(len, out)), t0
    for c in out:
        d = (t1 - t0) * len(c) / total
        yield t, t + d, c; t += d


def main(ep_path, out, dry=False):
    ep = json.load(open(ep_path, encoding='utf-8'))
    errs = validate(ep)
    if errs: sys.exit('Invalid episode:\n' + '\n'.join(errs))
    os.makedirs(out, exist_ok=True)
    t, clips, lines, scenes, subs = int(0.5 * SR), [], [], [], []
    frame = lambda s: s // HOP + 1
    for si, sc in enumerate(ep['scenes']):
        s0 = t
        for li, ln in enumerate(sc['lines']):
            a = tts(ln['text'], ln['who'], dry)
            n = len(a) // HOP
            env = np.sqrt((a[:n * HOP].reshape(n, HOP) ** 2).mean(1)) if n else np.zeros(1)
            env = np.clip(env / max(np.percentile(env, 95), 1e-4), 0, 1) if not dry else (np.sin(np.arange(n) * 0.9) * 0.5 + 0.5)
            clips.append((t, a))
            lines.append(dict(scene=si, idx=li, start=frame(t), end=frame(t + len(a)), mouth=[round(float(x), 2) for x in env]))
            subs += cues(ln['text'], t / SR, (t + len(a)) / SR)
            t += len(a) + int(0.35 * SR)
        t += int(0.6 * SR)
        scenes.append(dict(start=frame(s0), end=frame(t) - 1))
    t += int(1.5 * SR)
    scenes[0]['start'], scenes[-1]['end'] = 1, frame(t)
    for a, b in zip(scenes, scenes[1:]): a['end'] = b['start'] - 1
    total = frame(t)
    track = np.zeros(t, 'f4')
    for s, a in clips: track[s:s + len(a)] += a
    import soundfile as sf
    sf.write(f'{out}/dialogue.wav', np.clip(track, -1, 1), SR, subtype='PCM_16')
    with open(f'{out}/subs.srt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{c}\n' for i, (a, b, c) in enumerate(subs, 1)))
    chunks = [[a, min(a + CHUNK - 1, total)] for a in range(1, total + 1, CHUNK)]
    json.dump(dict(fps=FPS, frames=total, scenes=scenes, lines=lines, chunks=chunks), open(f'{out}/timeline.json', 'w'))
    print(f'{total} frames ({total / FPS / 60:.1f} min), {len(chunks)} render chunks')
    if os.environ.get('GITHUB_OUTPUT'):
        open(os.environ['GITHUB_OUTPUT'], 'a').write(f'chunks={json.dumps(list(range(len(chunks))))}\n')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], '--dry' in sys.argv)
