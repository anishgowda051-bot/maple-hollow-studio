"""Maple Hollow: the one source of truth for cast, places, props, actions.
Shared by check.py (writer validation), voice.py and render.py (Blender)."""

FPS = 24

COLORS = {
    'white': '#FFFFFF', 'cream': '#FFF0D9', 'black': '#1E1A2E', 'dark': '#3A2A22', 'mouth': '#5A1E2A',
    'orange': '#F08A24', 'orange2': '#D9701A', 'purple': '#8F6BD6', 'lavender': '#E2D4FA', 'yellow': '#F5B53D',
    'teal': '#2EC4B6', 'steel': '#DDE6EC', 'navy': '#2B3A42', 'pink': '#F7A1C4', 'pink2': '#FFC9DD',
    'rose': '#E5547A', 'red': '#E84A4A', 'blue': '#3E7BE6', 'green': '#5FB85A', 'turtle': '#8CCB7E',
    'shell': '#9C6B3C', 'shell2': '#C9955B', 'belly': '#E9D9A6', 'bark': '#8A5A3B', 'leaf': '#5DBB4F',
    'leaf2': '#7DD35F', 'pine': '#2F8F57', 'rock': '#A3ABB5', 'sand': '#F2D49B', 'snow': '#F3F7FF',
    'gold': '#F2C14E', 'paper': '#F4E9CF', 'wall': '#F6E7C8', 'roof': '#D2553F', 'window': '#9FD3F0',
    'moonrock': '#B9B9C9', 'crater': '#9C9CB0', 'mountain': '#8E9AAF', 'hill': '#8CCB74', 'water': '#3FA9D6',
    # emissive
    'glow': '#FFD93D', 'highlight': '#FFFFFF', 'flame': '#FF8A2B', 'lit': '#FFD98A', 'star': '#FFF6D5', 'moon': '#F4F1DE',
}
GLOW = {'glow', 'highlight', 'flame', 'lit', 'star', 'moon'}
FLOWERS = ['#FF6B9A', '#FFD23F', '#FFFFFF', '#B07CFF', '#FF8C42']

# voice = kokoro voice id (first letter a/b = American/British); pitch >1 = younger; fx = extra ffmpeg filter
NARRATOR = dict(voice='bf_emma', speed=0.95, pitch=1.0)

# part = (group, shape, size, loc, color[, rot]); loc is relative to the group pivot.
# face = eye x/y/z + radius, mouth y/z (relative to head pivot).
CAST = {
    'milo': dict(
        name='Milo', about='a curious, brave, sometimes too-impatient young fox', voice='am_puck', speed=1.05, pitch=1.18,
        pivots={'head': (0, 0, 1.0), 'arm_l': (-0.36, 0, 0.85), 'arm_r': (0.36, 0, 0.85), 'tail': (0, 0.3, 0.45)},
        face=dict(ex=0.16, ey=-0.31, ez=0.42, er=0.11, my=-0.42, mz=0.1),
        parts=[
            ('body', 'sphere', (0.38, 0.34, 0.48), (0, 0, 0.55), 'orange'),
            ('body', 'sphere', (0.27, 0.18, 0.34), (0, -0.2, 0.5), 'cream'),
            ('body', 'sphere', (0.13, 0.15, 0.12), (-0.18, -0.05, 0.08), 'orange2'),
            ('body', 'sphere', (0.13, 0.15, 0.12), (0.18, -0.05, 0.08), 'orange2'),
            ('tail', 'sphere', (0.16, 0.16, 0.42), (0, 0.15, 0.2), 'orange', (-0.9, 0, 0)),
            ('tail', 'sphere', (0.11, 0.11, 0.15), (0, 0.38, 0.5), 'cream', (-0.9, 0, 0)),
            ('head', 'sphere', (0.44, 0.4, 0.38), (0, 0, 0.32), 'orange'),
            ('head', 'sphere', (0.22, 0.16, 0.14), (0, -0.32, 0.2), 'cream'),
            ('head', 'sphere', (0.07, 0.06, 0.055), (0, -0.47, 0.26), 'dark'),
            ('head', 'cone', (0.15, 0.1, 0.26), (-0.25, 0, 0.68), 'orange', (0, -0.35, 0)),
            ('head', 'cone', (0.15, 0.1, 0.26), (0.25, 0, 0.68), 'orange', (0, 0.35, 0)),
            ('head', 'cone', (0.08, 0.05, 0.16), (-0.24, -0.07, 0.64), 'dark', (0, -0.35, 0)),
            ('head', 'cone', (0.08, 0.05, 0.16), (0.24, -0.07, 0.64), 'dark', (0, 0.35, 0)),
            ('arm_l', 'sphere', (0.09, 0.09, 0.24), (0, 0, -0.2), 'orange'),
            ('arm_r', 'sphere', (0.09, 0.09, 0.24), (0, 0, -0.2), 'orange'),
        ]),
    'luna': dict(
        name='Luna', about='a thoughtful, book-loving owl who worries a lot but is very kind', voice='af_sky', speed=1.0, pitch=1.15,
        pivots={'head': (0, 0, 1.15), 'arm_l': (-0.45, 0, 0.95), 'arm_r': (0.45, 0, 0.95)},
        face=dict(ex=0.18, ey=-0.3, ez=0.28, er=0.14, my=-0.34, mz=0.0),
        parts=[
            ('body', 'sphere', (0.48, 0.42, 0.6), (0, 0, 0.65), 'purple'),
            ('body', 'sphere', (0.33, 0.2, 0.42), (0, -0.26, 0.58), 'lavender'),
            ('body', 'sphere', (0.1, 0.12, 0.05), (-0.15, -0.2, 0.04), 'yellow'),
            ('body', 'sphere', (0.1, 0.12, 0.05), (0.15, -0.2, 0.04), 'yellow'),
            ('head', 'sphere', (0.46, 0.4, 0.38), (0, 0, 0.22), 'purple'),
            ('head', 'sphere', (0.2, 0.07, 0.2), (-0.18, -0.27, 0.28), 'lavender'),
            ('head', 'sphere', (0.2, 0.07, 0.2), (0.18, -0.27, 0.28), 'lavender'),
            ('head', 'cone', (0.06, 0.05, 0.1), (0, -0.42, 0.16), 'yellow', (3.1, 0, 0)),
            ('head', 'cone', (0.1, 0.07, 0.2), (-0.3, 0, 0.58), 'purple', (0, -0.5, 0)),
            ('head', 'cone', (0.1, 0.07, 0.2), (0.3, 0, 0.58), 'purple', (0, 0.5, 0)),
            ('arm_l', 'sphere', (0.12, 0.08, 0.32), (0, 0, -0.22), 'purple'),
            ('arm_r', 'sphere', (0.12, 0.08, 0.32), (0, 0, -0.22), 'purple'),
        ]),
    'bolt': dict(
        name='Bolt', about='a small, funny robot who takes everything literally and is learning about feelings', voice='am_echo', speed=1.0, pitch=1.08,
        fx='aecho=0.8:0.8:9:0.3',
        pivots={'head': (0, 0, 1.02), 'arm_l': (-0.42, 0, 0.88), 'arm_r': (0.42, 0, 0.88)},
        face=dict(ex=0.12, ey=-0.33, ez=0.34, er=0.085, my=-0.34, mz=0.2, brow='steel'),
        parts=[
            ('body', 'rcube', (0.36, 0.3, 0.38), (0, 0, 0.62), 'teal'),
            ('body', 'rcube', (0.22, 0.04, 0.16), (0, -0.3, 0.66), 'steel'),
            ('body', 'sphere', (0.05, 0.05, 0.05), (0, -0.34, 0.72), 'glow'),
            ('body', 'cyl', (0.09, 0.09, 0.12), (-0.16, 0, 0.14), 'navy'),
            ('body', 'cyl', (0.09, 0.09, 0.12), (0.16, 0, 0.14), 'navy'),
            ('body', 'rcube', (0.12, 0.16, 0.05), (-0.16, -0.04, 0.04), 'navy'),
            ('body', 'rcube', (0.12, 0.16, 0.05), (0.16, -0.04, 0.04), 'navy'),
            ('head', 'rcube', (0.38, 0.32, 0.3), (0, 0, 0.3), 'steel'),
            ('head', 'rcube', (0.3, 0.02, 0.2), (0, -0.32, 0.3), 'navy'),
            ('head', 'cyl', (0.02, 0.02, 0.18), (0, 0, 0.75), 'navy'),
            ('head', 'sphere', (0.07, 0.07, 0.07), (0, 0, 0.95), 'glow'),
            ('head', 'cyl', (0.07, 0.07, 0.05), (-0.4, 0, 0.3), 'teal', (0, 1.5708, 0)),
            ('head', 'cyl', (0.07, 0.07, 0.05), (0.4, 0, 0.3), 'teal', (0, 1.5708, 0)),
            ('arm_l', 'cyl', (0.06, 0.06, 0.22), (0, 0, -0.2), 'teal'),
            ('arm_r', 'cyl', (0.06, 0.06, 0.22), (0, 0, -0.2), 'teal'),
            ('arm_l', 'sphere', (0.08, 0.08, 0.08), (0, 0, -0.44), 'steel'),
            ('arm_r', 'sphere', (0.08, 0.08, 0.08), (0, 0, -0.44), 'steel'),
        ]),
    'pepper': dict(
        name='Pepper', about='an energetic, sporty, very competitive bunny who hates losing', voice='af_nova', speed=1.08, pitch=1.2,
        pivots={'head': (0, 0, 0.95), 'arm_l': (-0.33, 0, 0.78), 'arm_r': (0.33, 0, 0.78), 'tail': (0, 0.3, 0.4)},
        face=dict(ex=0.13, ey=-0.27, ez=0.36, er=0.1, my=-0.35, mz=0.1),
        parts=[
            ('body', 'sphere', (0.36, 0.32, 0.45), (0, 0, 0.52), 'pink'),
            ('body', 'sphere', (0.25, 0.17, 0.32), (0, -0.2, 0.48), 'white'),
            ('body', 'sphere', (0.13, 0.2, 0.08), (-0.16, -0.08, 0.06), 'white'),
            ('body', 'sphere', (0.13, 0.2, 0.08), (0.16, -0.08, 0.06), 'white'),
            ('tail', 'sphere', (0.13, 0.13, 0.13), (0, 0.05, 0), 'white'),
            ('head', 'sphere', (0.38, 0.35, 0.34), (0, 0, 0.3), 'pink'),
            ('head', 'sphere', (0.15, 0.1, 0.1), (0, -0.3, 0.18), 'white'),
            ('head', 'sphere', (0.045, 0.04, 0.035), (0, -0.39, 0.24), 'rose'),
            ('head', 'cyl', (0.32, 0.295, 0.035), (0, 0, 0.5), 'red'),
            ('head', 'sphere', (0.1, 0.06, 0.36), (-0.15, 0.02, 0.9), 'pink', (0, -0.15, 0)),
            ('head', 'sphere', (0.1, 0.06, 0.36), (0.15, 0.02, 0.9), 'pink', (0, 0.15, 0)),
            ('head', 'sphere', (0.06, 0.03, 0.28), (-0.155, -0.03, 0.9), 'pink2', (0, -0.15, 0)),
            ('head', 'sphere', (0.06, 0.03, 0.28), (0.155, -0.03, 0.9), 'pink2', (0, 0.15, 0)),
            ('arm_l', 'sphere', (0.08, 0.08, 0.2), (0, 0, -0.17), 'pink'),
            ('arm_r', 'sphere', (0.08, 0.08, 0.2), (0, 0, -0.17), 'pink'),
        ]),
    'grandpa': dict(
        name='Grandpa Shell', about='a gentle, wise old turtle who tells funny stories from long ago', voice='bm_george', speed=0.9, pitch=0.92,
        pivots={'head': (0, -0.1, 0.95), 'arm_l': (-0.5, -0.05, 0.75), 'arm_r': (0.5, -0.05, 0.75)},
        face=dict(ex=0.12, ey=-0.31, ez=0.28, er=0.09, my=-0.35, mz=0.12, brow='white'),
        parts=[
            ('body', 'sphere', (0.55, 0.5, 0.45), (0, 0.1, 0.55), 'shell'),
            ('body', 'sphere', (0.17, 0.17, 0.08), (-0.22, 0.3, 0.9), 'shell2', (0.5, -0.4, 0)),
            ('body', 'sphere', (0.17, 0.17, 0.08), (0.22, 0.3, 0.9), 'shell2', (0.5, 0.4, 0)),
            ('body', 'sphere', (0.17, 0.17, 0.08), (0, 0.5, 0.7), 'shell2', (1.1, 0, 0)),
            ('body', 'sphere', (0.42, 0.2, 0.4), (0, -0.25, 0.5), 'belly'),
            ('body', 'sphere', (0.15, 0.15, 0.14), (-0.25, -0.1, 0.1), 'turtle'),
            ('body', 'sphere', (0.15, 0.15, 0.14), (0.25, -0.1, 0.1), 'turtle'),
            ('head', 'sphere', (0.32, 0.3, 0.3), (0, -0.08, 0.22), 'turtle'),
            ('head', 'torus', (0.11, 0.015), (-0.12, -0.36, 0.28), 'dark', (1.5708, 0, 0)),
            ('head', 'torus', (0.11, 0.015), (0.12, -0.36, 0.28), 'dark', (1.5708, 0, 0)),
            ('head', 'sphere', (0.15, 0.06, 0.045), (0, -0.37, 0.17), 'white'),
            ('arm_l', 'sphere', (0.1, 0.1, 0.22), (0, 0, -0.18), 'turtle'),
            ('arm_r', 'sphere', (0.1, 0.1, 0.22), (0, 0, -0.18), 'turtle'),
        ]),
}

# prop = list of (shape, size, loc, color[, rot]); 'flower' color = random pick from FLOWERS
PROPS = {
    'tree': [('cyl', (0.15, 0.15, 0.6), (0, 0, 0.6), 'bark'), ('sphere', (0.8, 0.8, 0.75), (0, 0, 1.7), 'leaf'),
             ('sphere', (0.55, 0.55, 0.5), (0.35, 0.2, 2.2), 'leaf2')],
    'big_tree': [('cyl', (0.35, 0.35, 1.6), (0, 0, 1.6), 'bark'), ('sphere', (1.8, 1.6, 1.5), (0, 0, 4.0), 'leaf'),
                 ('sphere', (1.2, 1.1, 1.0), (1.1, 0.3, 4.9), 'leaf2'), ('sphere', (1.1, 1.0, 1.0), (-1.2, 0.2, 4.6), 'leaf2')],
    'apple_tree': [('cyl', (0.15, 0.15, 0.6), (0, 0, 0.6), 'bark'), ('sphere', (0.8, 0.8, 0.75), (0, 0, 1.7), 'leaf'),
                   ('sphere', (0.09,) * 3, (0.5, -0.5, 1.6), 'red'), ('sphere', (0.09,) * 3, (-0.4, -0.6, 1.9), 'red'),
                   ('sphere', (0.09,) * 3, (0.1, -0.75, 1.4), 'red')],
    'pine': [('cyl', (0.12, 0.12, 0.4), (0, 0, 0.4), 'bark'), ('cone', (0.75, 0.75, 0.9), (0, 0, 1.3), 'pine'),
             ('cone', (0.55, 0.55, 0.7), (0, 0, 2.0), 'pine')],
    'snowpine': [('cyl', (0.12, 0.12, 0.4), (0, 0, 0.4), 'bark'), ('cone', (0.75, 0.75, 0.9), (0, 0, 1.3), 'pine'),
                 ('cone', (0.55, 0.55, 0.7), (0, 0, 2.0), 'pine'), ('cone', (0.3, 0.3, 0.35), (0, 0, 2.45), 'snow')],
    'palm': [('cyl', (0.13, 0.13, 1.4), (0.2, 0, 1.4), 'shell2', (0, 0.15, 0)),
             ('sphere', (1.0, 0.3, 0.08), (0.9, 0, 2.75), 'leaf', (0, 0.4, 0)), ('sphere', (1.0, 0.3, 0.08), (-0.4, 0, 2.75), 'leaf', (0, -0.4, 0)),
             ('sphere', (0.3, 1.0, 0.08), (0.3, 0.7, 2.75), 'leaf2', (-0.4, 0, 0)), ('sphere', (0.3, 1.0, 0.08), (0.3, -0.7, 2.75), 'leaf2', (0.4, 0, 0))],
    'bush': [('sphere', (0.5, 0.45, 0.4), (0, 0, 0.3), 'leaf'), ('sphere', (0.35, 0.3, 0.3), (0.35, 0.1, 0.25), 'leaf2')],
    'flower': [('cyl', (0.02, 0.02, 0.15), (0, 0, 0.15), 'leaf'), ('sphere', (0.09, 0.09, 0.04), (0, 0, 0.31), 'flower')],
    'rock': [('ico', (0.4, 0.35, 0.25), (0, 0, 0.1), 'rock')],
    'mushroom': [('cyl', (0.06, 0.06, 0.12), (0, 0, 0.12), 'cream'), ('sphere', (0.18, 0.18, 0.1), (0, 0, 0.26), 'red')],
    'shell_small': [('sphere', (0.12, 0.1, 0.05), (0, 0, 0.03), 'pink2')],
    'cloud': [('sphere', (1.6, 1.0, 0.9), (0, 0, 0), 'white'), ('sphere', (1.1, 0.9, 0.8), (1.4, 0, -0.2), 'white'),
              ('sphere', (1.0, 0.8, 0.7), (-1.4, 0, -0.25), 'white')],
    'house': [('rcube', (1.0, 0.9, 0.8), (0, 0, 0.8), 'wall'), ('pyramid', (1.45, 1.35, 0.7), (0, 0, 2.3), 'roof'),
              ('rcube', (0.22, 0.05, 0.38), (0, -0.9, 0.38), 'bark'), ('rcube', (0.18, 0.04, 0.18), (-0.55, -0.9, 1.05), 'window'),
              ('rcube', (0.18, 0.04, 0.18), (0.55, -0.9, 1.05), 'window')],
    'lamp': [('cyl', (0.05, 0.05, 0.9), (0, 0, 0.9), 'navy'), ('sphere', (0.15,) * 3, (0, 0, 1.9), 'lit')],
    'snowman': [('sphere', (0.5,) * 3, (0, 0, 0.45), 'snow'), ('sphere', (0.36,) * 3, (0, 0, 1.15), 'snow'),
                ('sphere', (0.26,) * 3, (0, 0, 1.68), 'snow'), ('cone', (0.05, 0.05, 0.18), (0, -0.35, 1.68), 'orange', (1.5708, 0, 0))],
    'crater': [('sphere', (0.9, 0.9, 0.06), (0, 0, 0.0), 'crater')],
    'hill': [('sphere', (14, 8, 4), (0, 0, -1), 'hill')],
    'mountain': [('cone', (9, 9, 7), (0, 0, 6), 'mountain'), ('cone', (2.6, 2.6, 2.0), (0, 0, 11.0), 'snow')],
    # story props
    'kite': [('cube', (0.4, 0.03, 0.4), (0, 0, 0), 'red', (0, 0.785, 0)), ('cyl', (0.015, 0.015, 0.55), (0, -0.02, -0.55), 'dark'),
             ('sphere', (0.06,) * 3, (0, -0.02, -0.75), 'yellow'), ('sphere', (0.06,) * 3, (0, -0.02, -1.0), 'blue')],
    'ball': [('sphere', (0.25,) * 3, (0, 0, 0.25), 'red')],
    'book': [('rcube', (0.25, 0.18, 0.05), (0, 0, 0.05), 'blue'), ('rcube', (0.23, 0.165, 0.04), (0, -0.005, 0.1), 'paper')],
    'chest': [('rcube', (0.45, 0.3, 0.25), (0, 0, 0.25), 'bark'), ('rcube', (0.47, 0.32, 0.08), (0, 0, 0.52), 'gold'),
              ('rcube', (0.06, 0.03, 0.08), (0, -0.32, 0.4), 'gold')],
    'map': [('rcube', (0.45, 0.32, 0.012), (0, 0, 0.02), 'paper'), ('sphere', (0.05, 0.05, 0.01), (0.2, -0.1, 0.035), 'red')],
    'cake': [('cyl', (0.35, 0.35, 0.18), (0, 0, 0.18), 'pink'), ('cyl', (0.25, 0.25, 0.12), (0, 0, 0.45), 'cream'),
             ('cyl', (0.02, 0.02, 0.08), (0, 0, 0.65), 'blue'), ('sphere', (0.03, 0.03, 0.05), (0, 0, 0.77), 'flame')],
    'campfire': [('cyl', (0.07, 0.07, 0.4), (0, 0, 0.07), 'bark', (0, 1.5708, 0.5)), ('cyl', (0.07, 0.07, 0.4), (0, 0, 0.07), 'bark', (0, 1.5708, -0.5)),
                 ('cone', (0.2, 0.2, 0.35), (0, 0, 0.38), 'flame'), ('cone', (0.12, 0.12, 0.22), (0, 0, 0.62), 'glow')],
    'tent': [('pyramid', (1.0, 1.0, 1.0), (0, 0, 1.0), 'orange'), ('pyramid', (0.35, 0.05, 0.5), (0, -0.72, 0.5), 'dark')],
    'rocket': [('cyl', (0.4, 0.4, 1.0), (0, 0, 1.2), 'white'), ('cone', (0.4, 0.4, 0.6), (0, 0, 2.8), 'red'),
               ('sphere', (0.15, 0.05, 0.15), (0, -0.38, 1.6), 'window'), ('cone', (0.25, 0.25, 0.3), (0, 0, 0.1), 'flame', (3.1416, 0, 0)),
               ('rcube', (0.05, 0.4, 0.35), (0.45, 0, 0.5), 'red'), ('rcube', (0.05, 0.4, 0.35), (-0.45, 0, 0.5), 'red')],
    'bench': [('rcube', (0.9, 0.25, 0.05), (0, 0, 0.45), 'bark'), ('rcube', (0.06, 0.2, 0.2), (-0.75, 0, 0.2), 'navy'),
              ('rcube', (0.06, 0.2, 0.2), (0.75, 0, 0.2), 'navy')],
    'lantern': [('rcube', (0.15, 0.15, 0.2), (0, 0, 0.2), 'lit'), ('cone', (0.18, 0.18, 0.1), (0, 0, 0.5), 'navy')],
    'sign': [('cyl', (0.05, 0.05, 0.6), (0, 0, 0.6), 'bark'), ('rcube', (0.5, 0.05, 0.25), (0, -0.06, 1.1), 'paper')],
    'bridge': [('rcube', (1.6, 0.7, 0.08), (0, 0, 0.35), 'bark'), ('rcube', (1.6, 0.04, 0.04), (0, -0.65, 0.75), 'bark'),
               ('rcube', (1.6, 0.04, 0.04), (0, 0.65, 0.75), 'bark')],
    'boat': [('sphere', (0.9, 0.42, 0.25), (0, 0, 0.12), 'bark'), ('cyl', (0.03, 0.03, 0.7), (0, 0, 0.8), 'dark'),
             ('cone', (0.45, 0.03, 0.55), (0.25, 0, 0.85), 'white')],
    'gift': [('rcube', (0.3, 0.3, 0.3), (0, 0, 0.3), 'red'), ('rcube', (0.32, 0.06, 0.32), (0, 0, 0.3), 'gold'),
             ('rcube', (0.06, 0.32, 0.32), (0, 0, 0.3), 'gold')],
    'trophy': [('cyl', (0.2, 0.2, 0.06), (0, 0, 0.06), 'navy'), ('cyl', (0.05, 0.05, 0.15), (0, 0, 0.25), 'gold'),
               ('sphere', (0.22, 0.22, 0.2), (0, 0, 0.5), 'gold')],
    'telescope': [('cyl', (0.08, 0.08, 0.45), (0, 0, 1.0), 'gold', (0.9, 0, 0)), ('cyl', (0.025, 0.025, 0.5), (0, 0, 0.5), 'dark')],
    'balloon': [('sphere', (0.3, 0.3, 0.36), (0, 0, 2.2), 'red'), ('cyl', (0.008, 0.008, 0.9), (0, 0, 1.0), 'white')],
    'basket': [('cyl', (0.3, 0.3, 0.15), (0, 0, 0.15), 'shell2'), ('sphere', (0.1,) * 3, (0.1, 0, 0.32), 'red'),
               ('sphere', (0.1,) * 3, (-0.1, 0.05, 0.32), 'red')],
    'sandcastle': [('cyl', (0.5, 0.5, 0.2), (0, 0, 0.2), 'sand'), ('cyl', (0.15, 0.15, 0.3), (-0.3, 0, 0.6), 'sand'),
                   ('cyl', (0.15, 0.15, 0.3), (0.3, 0, 0.6), 'sand'), ('cone', (0.18, 0.18, 0.2), (-0.3, 0, 1.1), 'sand'),
                   ('cone', (0.18, 0.18, 0.2), (0.3, 0, 1.1), 'sand')],
}
STORY_PROPS = sorted(k for k in PROPS if k not in {'tree', 'pine', 'snowpine', 'palm', 'bush', 'flower', 'rock', 'mushroom',
                                                    'shell_small', 'cloud', 'house', 'lamp', 'snowman', 'crater', 'hill', 'mountain'})
STORY_PROPS += ['tree', 'house', 'snowman', 'rock', 'bush']
PROP_SPOTS = {'left': (-3.0, 0.8, 0), 'right': (3.0, 0.8, 0), 'center': (0, 2.2, 0), 'front': (0.9, -1.1, 0),
              'back': (0, 6.0, 0), 'sky': (1.4, 4.3, 3.6)}

# scatter = (prop, count); water = y where water starts (None = no water)
SETTINGS = {
    'meadow': dict(ground='#7DC66A', scatter=[('tree', 10), ('bush', 10), ('flower', 70), ('rock', 6), ('cloud', 6), ('hill', 5)]),
    'forest': dict(ground='#5DA35A', scatter=[('pine', 30), ('tree', 10), ('mushroom', 16), ('bush', 8), ('rock', 6), ('hill', 4)]),
    'riverside': dict(ground='#79C268', water=4.5, scatter=[('tree', 8), ('bush', 8), ('flower', 40), ('rock', 12), ('cloud', 5)]),
    'beach': dict(ground='#F2D49B', water=5.0, scatter=[('palm', 8), ('shell_small', 25), ('rock', 5), ('cloud', 6)]),
    'snow': dict(ground='#F3F7FF', scatter=[('snowpine', 28), ('snowman', 1), ('rock', 5), ('mountain', 4)]),
    'village': dict(ground='#86C36E', scatter=[('house', 8), ('tree', 8), ('lamp', 6), ('flower', 40), ('bush', 6), ('cloud', 5), ('hill', 4)]),
    'mountains': dict(ground='#8FBF73', scatter=[('mountain', 6), ('pine', 18), ('rock', 14), ('cloud', 5)]),
    'moon': dict(ground='#B9B9C9', night=True, scatter=[('crater', 22), ('rock', 10)]),
}
TIMES = {  # horizon, zenith, sun color, sun strength, sun elevation (deg), world strength
    'day': ('#A8DCFF', '#3D8BF2', '#FFF4E0', 3.2, 50, 0.9),
    'sunset': ('#FFB37A', '#7357D9', '#FFB070', 2.6, 14, 0.7),
    'night': ('#2B3A6B', '#0B1030', '#AFC4FF', 0.9, 40, 0.35),
}

ACTIONS = ['jump', 'wave', 'nod', 'shake', 'spin', 'laugh', 'shrug', 'point', 'think', 'dance', 'sad', 'surprised', 'cheer']
EMOTIONS = {  # brow raise, inner-brow tilt (+ = angry, - = worried), mouth width
    'neutral': (0, 0, 1.0), 'happy': (0.02, 0, 1.25), 'excited': (0.05, 0, 1.35), 'proud': (0.02, 0, 1.2),
    'sad': (0, -0.35, 0.8), 'worried': (0.03, -0.3, 0.9), 'scared': (0.06, -0.3, 0.8), 'angry': (-0.02, 0.35, 0.95),
    'surprised': (0.08, 0, 0.85), 'thinking': (0.03, 0.15, 0.9), 'silly': (0.04, 0.2, 1.3),
}
