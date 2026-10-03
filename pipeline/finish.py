"""Editor + QA bot: chunks -> final 1080p episode with music, thumbnail, Short, metadata, QA report.
Usage: python pipeline/finish.py episodes/ep001.json work/   (expects work/chunks/*.mp4 + thumb.png, voice outputs)"""
import glob, json, os, random, re, shutil, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from world import CAST

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, 'assets', 'fonts')


def ff(*args): subprocess.run(['ffmpeg', '-y', '-v', 'error', *args], check=True)


def make_music(path, rng, secs=40, sr=44100):
    """Gentle music-box loop (C-G-Am-F, random key/tempo per episode). Royalty-free by construction."""
    bpm, shift = rng.randint(88, 108), rng.randint(-3, 4)
    step = 30 / bpm  # eighth notes
    n = int(secs / step) // 32 * 32
    total = int(n * step * sr)
    out = np.zeros(total)
    chords = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]
    pattern = [0, 1, 2, 3, 2, 1, 2, 3]
    for i in range(n):
        ch = chords[i // 8 % 4]
        for midi, amp, dec, length in ([(ch[pattern[i % 8]] + 12 + shift, .16, 4.5, 1.2)] +
                                       ([(ch[0] - 12 + shift, .12, 1.2, 2.4)] if i % 8 == 0 else [])):
            t = np.arange(int(sr * length)) / sr
            f = 440 * 2 ** ((midi - 69) / 12)
            tone = np.exp(-t * dec) * (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t) + .1 * np.sin(6 * np.pi * f * t)) * amp
            idx = (int(i * step * sr) + np.arange(len(t))) % total  # wrap tails -> seamless loop
            np.add.at(out, idx, tone)
    import soundfile as sf
    sf.write(path, (out / np.abs(out).max() * 0.5).astype('f4'), sr)


def thumbnail(src, text, dst):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.open(src).convert('RGB').resize((1280, 720))
    size = 190
    while True:
        f = ImageFont.truetype(os.path.join(FONTS, 'LuckiestGuy.ttf'), size)
        if f.getbbox(text.upper())[2] < 760 or size < 70: break
        size -= 8
    layer = Image.new('RGBA', img.size)
    d = ImageDraw.Draw(layer)
    d.text((50, 40), text.upper(), font=f, fill='#FFD23F', stroke_width=max(8, size // 14), stroke_fill='#2B1B4A')
    d.text((1240, 690), 'MAPLE HOLLOW', font=ImageFont.truetype(os.path.join(FONTS, 'LuckiestGuy.ttf'), 40),
           fill='white', stroke_width=5, stroke_fill='#2B1B4A', anchor='rb')
    layer = layer.rotate(4, resample=Image.BICUBIC, center=(400, 150))
    img.paste(layer, (0, 0), layer)
    img.save(dst, quality=90)


def qa(video, expected):
    err = subprocess.run(['ffmpeg', '-i', video, '-vf', 'blackdetect=d=1.0:pix_th=0.05', '-af', 'volumedetect', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout)
    mean = float(re.search(r'mean_volume: ([-\d.]+)', err).group(1))
    blacks = re.findall(r'black_duration:([\d.]+)', err)
    return {f'Length {dur / 60:.1f} min matches script': abs(dur - expected) < 1.5,
            'At least 1 minute long': dur >= 60,
            f'No black gaps ({len(blacks)} found)': not blacks,
            f'Audio level OK (mean {mean:.0f} dB)': -32 < mean < -8}


def review_md(ep, checks, dst):
    repo, tag = os.environ.get('GITHUB_REPOSITORY', 'owner/repo'), os.environ.get('TAG', '')
    owner, name = repo.split('/')
    dl = f'https://github.com/{repo}/releases/download/{tag}'
    script = '\n'.join(f"**{'Narrator' if l['who'] == 'narrator' else CAST[l['who']]['name']}:** {l['text']}  " for s in ep['scenes'] for l in s['lines'])
    ticks = '\n'.join(('- ✅ ' if v else '- ❌ ') + k for k, v in checks.items())
    open(dst, 'w', encoding='utf-8').write(f"""## 🎬 {ep['title']}
**Lesson:** {ep['lesson']}

<img src="https://raw.githubusercontent.com/{repo}/main/docs/thumbs/{ep['id']}.jpg" width="480">

▶️ **[Watch in the review player](https://{owner}.github.io/{name}/#review)** · [episode.mp4]({dl}/episode.mp4) · [short.mp4]({dl}/short.mp4) · [thumbnail.jpg]({dl}/thumbnail.jpg)

### Quality checks
{ticks}

### Your call
- Looks good → add the label **approved**
- Needs changes → comment what to change, then add the label **redo** (the writer bot revises it and it gets re-rendered)

<details><summary>Full script</summary>

{script}
</details>
""")


def main(ep_path, work):
    ep = json.load(open(ep_path, encoding='utf-8'))
    tl = json.load(open(f'{work}/timeline.json'))
    out = f'{work}/out'; os.makedirs(out, exist_ok=True)
    fps, dur = tl['fps'], tl['frames'] / tl['fps']
    rng = random.Random(ep['id'])

    chunks = sorted(glob.glob(f'{work}/chunks/chunk_*.mp4'))
    assert len(chunks) == len(tl['chunks']), f"{len(chunks)} chunks rendered, {len(tl['chunks'])} expected"
    with open(f'{work}/chunks.txt', 'w') as f: f.write(''.join(f"file '{os.path.abspath(c)}'\n" for c in chunks))
    tracks = sorted(glob.glob(f'{ROOT}/music/*.mp3') + glob.glob(f'{ROOT}/music/*.wav'))
    music = rng.choice(tracks) if tracks else f'{work}/music.wav'
    if not tracks: make_music(music, rng)

    ff('-f', 'concat', '-safe', '0', '-i', f'{work}/chunks.txt', '-i', f'{work}/dialogue.wav', '-stream_loop', '-1', '-i', music,
       '-filter_complex',
       f'[0:v]scale=1920:1080:flags=lanczos,format=yuv420p[v];[1:a]aresample=48000,asplit=2[d][sc];'
       f'[2:a]aresample=48000,atrim=0:{dur:.2f},volume=0.35[m];[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=600[md];'
       f'[d][md]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]',
       '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-tune', 'animation',
       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{dur:.2f}', '-movflags', '+faststart', f'{out}/episode.mp4')

    s = tl['scenes'][ep.get('short_scene', 0)]
    t0, length = (s['start'] - 1) / fps, min(58, (s['end'] - s['start']) / fps)
    style = 'FontName=Fredoka,FontSize=13,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00402A1A,BorderStyle=1,Outline=2,Shadow=0,MarginV=70'
    ff('-i', f'{out}/episode.mp4', '-ss', f'{t0:.2f}', '-t', f'{length:.2f}',
       '-vf', f"crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,subtitles={work}/subs.srt:fontsdir={FONTS}:force_style='{style}'",
       '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'{out}/short.mp4')

    thumbnail(f'{work}/chunks/thumb.png', ep['thumbnail_text'], f'{out}/thumbnail.jpg')
    shutil.copy(f'{work}/subs.srt', f'{out}/captions.srt')

    starts = [(sc['start'] - 1) / fps for sc in tl['scenes']]
    chapters = ''
    if len(starts) >= 3 and all(b - a >= 10 for a, b in zip(starts, starts[1:] + [dur])):
        chapters = '\n'.join(f'{int(t // 60)}:{int(t % 60):02d} {sc["title"]}' for t, sc in zip([0] + starts[1:], ep['scenes']))
    cast = ', '.join(f"{c['name']} ({c['about'].split(' who')[0].split(',')[0]})" for c in CAST.values())
    desc = (f"{ep['description']}\n\n⭐ Today's lesson: {ep['lesson']}\n\n{chapters}\n\n"
            f"Welcome to Maple Hollow! Funny 3D adventures with real-life lessons for curious kids. Meet the friends: {cast}.\n\n"
            "#kidscartoon #storiesforkids #maplehollow").replace('\n\n\n\n', '\n\n')
    tags, base = [], ep.get('tags', []) + ['maple hollow', 'kids cartoon', 'animated stories for kids']
    for t in dict.fromkeys(base):
        if len(','.join(tags + [t])) <= 450: tags.append(t)
    meta = dict(title=ep['title'], description=desc, tags=tags,
                short_title=f"{ep['title'].split('|')[0].strip()} #Shorts"[:100],
                short_description=f"{ep['lesson']}\n\nFull episode on the channel!\n#shorts #kidscartoon #maplehollow")
    json.dump(meta, open(f'{out}/metadata.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    checks = qa(f'{out}/episode.mp4', dur)
    review_md(ep, checks, f'{work}/review.md')
    for k, v in checks.items(): print(('PASS ' if v else 'FAIL ') + k)
    if not all(checks.values()): sys.exit('QA failed')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
