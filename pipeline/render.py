"""Animator bot: builds the whole episode in Blender from episode + timeline, renders one chunk.
blender -b -P pipeline/render.py -- <episode.json> <timeline.json> <chunk-index | thumb | preview:F1,F2,..> <outdir>
Env: RES (1920x1080), SAMPLES (24)."""
import bpy, bmesh, sys, os, json, math, random
from mathutils import Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from world import *

argv = sys.argv[sys.argv.index('--') + 1:]
EP = json.load(open(argv[0], encoding='utf-8'))
TL = json.load(open(argv[1]))
MODE, OUT = argv[2], os.path.abspath(argv[3])
FONT = os.path.join(HERE, '..', 'assets', 'fonts', 'LuckiestGuy.ttf')
GAP = 1000.0  # x distance between scene sets
EXTRA = {'star': [('sphere', (0.35,) * 3, (0, 0, 0), 'star')], 'moon': [('sphere', (7,) * 3, (0, 0, 0), 'moon')]}

bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene
os.makedirs(OUT, exist_ok=True)


# ---------- materials & meshes ----------
def lin(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0]


_mats = {}
def mat(c):
    if c not in _mats:
        m = bpy.data.materials.new(c); m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']; rgb = lin(COLORS.get(c, c))
        b.inputs['Base Color'].default_value = rgb
        b.inputs['Roughness'].default_value = 0.08 if c == 'water' else 0.5
        b.inputs['Specular IOR Level'].default_value = 0.35
        if c in GLOW:
            b.inputs['Emission Color'].default_value = rgb; b.inputs['Emission Strength'].default_value = 3.0
            m.cycles.emission_sampling = 'NONE'  # glowy look only; as real lights they cost 10x render time
        _mats[c] = m
    return _mats[c]


def ground_mat(hexc):
    m = bpy.data.materials.new('ground'); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = 0.9
    tc, nz, ramp = nt.nodes.new('ShaderNodeTexCoord'), nt.nodes.new('ShaderNodeTexNoise'), nt.nodes.new('ShaderNodeValToRGB')
    nz.inputs['Scale'].default_value = 0.18
    base = lin(hexc)
    ramp.color_ramp.elements[0].color = [x * 0.8 for x in base[:3]] + [1]
    ramp.color_ramp.elements[1].color = [min(1, x * 1.08) for x in base[:3]] + [1]
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    return m


def _mesh(name, build, sharp=False):
    bm = bmesh.new(); build(bm)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.shade_smooth()
    if sharp: me.set_sharp_from_angle(angle=0.9)
    me.materials.append(None)
    return me


def _pyramid(bm):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=1.414, radius2=0, depth=2)
    bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(math.pi / 4, 3, 'Z'))


MESH = {
    'sphere': _mesh('sphere', lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1)),
    'ico': _mesh('ico', lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1), sharp=True),
    'cone': _mesh('cone', lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=1, radius2=0, depth=2), sharp=True),
    'cyl': _mesh('cyl', lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=1, radius2=1, depth=2), sharp=True),
    'cube': _mesh('cube', lambda bm: bmesh.ops.create_cube(bm, size=2), sharp=True),
    'pyramid': _mesh('pyramid', _pyramid, sharp=True),
}
_cache = {}


def rcube(size):
    if ('r', size) not in _cache:
        def build(bm):
            bmesh.ops.create_cube(bm, size=2)
            bmesh.ops.scale(bm, vec=size, verts=bm.verts)
            bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=min(size) * 0.35, segments=4, affect='EDGES', profile=0.5, clamp_overlap=True)
        _cache['r', size] = _mesh('rcube', build)
    return _cache['r', size]


def torus(size):
    if ('t', size) not in _cache:
        R, r = size
        def build(bm):
            ring = [[bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
                     for b in [j * math.tau / 10 for j in range(10)]] for a in [i * math.tau / 32 for i in range(32)]]
            for i in range(32):
                for j in range(10):
                    bm.faces.new((ring[i][j], ring[(i + 1) % 32][j], ring[(i + 1) % 32][(j + 1) % 10], ring[i][(j + 1) % 10]))
        _cache['t', size] = _mesh('torus', build)
    return _cache['t', size]


def part(shape, size, loc, color, rot=(0, 0, 0), parent=None, coll=None):
    if shape == 'rcube': me, sc = rcube(tuple(size)), (1, 1, 1)
    elif shape == 'torus': me, sc = torus(tuple(size)), (1, 1, 1)
    else: me, sc = MESH[shape], size
    ob = bpy.data.objects.new(shape, me)
    (coll or SC.collection).objects.link(ob)
    ob.scale, ob.location, ob.rotation_euler, ob.parent = sc, loc, rot, parent
    ob.material_slots[0].link = 'OBJECT'; ob.material_slots[0].material = mat(color)
    return ob


def empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); SC.collection.objects.link(e)
    e.parent, e.location = parent, loc
    return e


_tpl = {}
def place(name, loc, rz=0.0, scale=1.0, night=False, rng=None):
    flower = rng.choice(FLOWERS) if name == 'flower' else None
    k = (name, flower, night)
    if k not in _tpl:
        c = _tpl[k] = bpy.data.collections.new('T_' + name)
        for shape, size, ploc, color, *rot in {**PROPS, **EXTRA}[name]:
            color = flower if color == 'flower' else ('lit' if color == 'window' and night else ('paper' if color == 'lit' and not night else color))
            ob = part(shape, size, ploc, color, rot[0] if rot else (0, 0, 0), coll=c)
            ob.visible_shadow = name != 'cloud'  # cloud shadows looked like dirt stripes
    e = empty(name, loc=loc); e.instance_type = 'COLLECTION'; e.instance_collection = _tpl[k]
    e.rotation_euler, e.scale = (0, 0, rz), (scale,) * 3
    return e


# ---------- keyframes ----------
INTERP = {}  # (object name, data_path) -> interpolation for all its keys


def key(ob, path, idx, f, v, interp=None):
    if idx is None: setattr(ob, path, v); ob.keyframe_insert(path, frame=f)
    else: getattr(ob, path)[idx] = v; ob.keyframe_insert(path, index=idx, frame=f)
    if interp: INTERP[ob.name, path] = interp


# ---------- sets ----------
def build_set(k, s):
    ox, st = k * GAP, SETTINGS[s['setting']]
    night = s.get('time') == 'night' or st.get('night', False)
    rng = random.Random(f"{EP['id']}-{k}")
    g = part('cyl', (160, 160, 0.05), (ox, 0, -0.05), 'rock'); g.material_slots[0].material = ground_mat(st['ground'])
    water = st.get('water')
    if water: part('cube', (160, 80, 0.04), (ox, water + 80, 0.0), 'water')
    for name, n in st['scatter']:
        for _ in range(n):
            if name == 'cloud': loc, sc = (ox + rng.uniform(-45, 45), rng.uniform(35, 75), rng.uniform(10, 17)), rng.uniform(1, 2.2)
            elif name in ('hill', 'mountain'): loc, sc = (ox + rng.uniform(-70, 70), rng.uniform(50, 90), 0), rng.uniform(0.8, 1.5)
            else:
                small = name in ('flower', 'shell_small', 'mushroom', 'rock', 'crater')
                for _try in range(30):
                    x, y = rng.uniform(-24, 24), rng.uniform(-7, 30)
                    if water and y > water - 0.6 and name != 'rock': continue
                    if abs(x) < 5.5 and y < 4.5: continue      # keep the stage clear
                    if y < 2 and (not small or abs(x) < 9): continue  # keep the camera path clear
                    break
                loc, sc = (ox + x, y, 0), rng.uniform(0.7, 1.35)
            place(name, loc, rng.uniform(0, math.tau), sc, night, rng)
    if night:
        for _ in range(160):
            place('star', (ox + rng.uniform(-160, 160), rng.uniform(90, 180), rng.uniform(12, 90)), 0, rng.uniform(0.5, 1.2))
        place('moon', (ox + 45, 170, 65))
    for i, pr in enumerate(s.get('props', [])):
        name, _, spot = pr.partition('@')
        x, y, z = PROP_SPOTS[spot or ('left', 'right', 'center')[i % 3]]
        place(name, (ox + x, y, z), 0, 1.0, night, rng)


def build_sky():
    w = bpy.data.worlds.new('sky'); SC.world = w; w.use_nodes = True; nt = w.node_tree; N = nt.nodes.new
    tc, sep, mr, mix, hz, zn = N('ShaderNodeTexCoord'), N('ShaderNodeSeparateXYZ'), N('ShaderNodeMapRange'), N('ShaderNodeMixRGB'), N('ShaderNodeRGB'), N('ShaderNodeRGB')
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = -0.02, 0.35
    L = nt.links.new
    L(tc.outputs['Generated'], sep.inputs[0]); L(sep.outputs['Z'], mr.inputs['Value']); L(mr.outputs['Result'], mix.inputs['Fac'])
    L(hz.outputs[0], mix.inputs['Color1']); L(zn.outputs[0], mix.inputs['Color2']); L(mix.outputs[0], nt.nodes['Background'].inputs['Color'])
    sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.angle = math.radians(4)
    sun = bpy.data.objects.new('sun', sun_d); SC.collection.objects.link(sun)
    bg = nt.nodes['Background']
    for k, s in enumerate(EP['scenes']):
        f = TL['scenes'][k]['start']
        t = 'night' if SETTINGS[s['setting']].get('night') else s.get('time', 'day')
        h, z, sc, se, el, ws = TIMES[t]
        for node, c in ((hz, h), (zn, z)): node.outputs[0].default_value = lin(c); node.outputs[0].keyframe_insert('default_value', frame=f)
        bg.inputs['Strength'].default_value = ws; bg.inputs['Strength'].keyframe_insert('default_value', frame=f)
        sun_d.color = lin(sc)[:3]; sun_d.keyframe_insert('color', frame=f)
        sun_d.energy = se; sun_d.keyframe_insert('energy', frame=f)
        sun.rotation_euler = (math.radians(90 - el), 0, math.radians(25)); sun.keyframe_insert('rotation_euler', frame=f)
    for idb in (nt, sun_d, sun):
        for fc in idb.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'


# ---------- characters ----------
def build_char(key_):
    c = CAST[key_]
    root = empty(key_); body = empty(key_ + '_body', root)
    piv = {'body': body}
    for g, loc in c['pivots'].items(): piv[g] = empty(f'{key_}_{g}', body, loc)
    for g, shape, size, loc, color, *rot in c['parts']: part(shape, size, loc, color, rot[0] if rot else (0, 0, 0), piv[g])
    f, head = c['face'], piv['head']; er = f['er']
    for side, sx in (('l', -1), ('r', 1)):
        e = piv['eye_' + side] = empty(f'{key_}_eye_{side}', head, (sx * f['ex'], f['ey'], f['ez']))
        part('sphere', (er, er * .7, er * 1.15), (0, 0, 0), 'white', parent=e)
        part('sphere', (er * .55, er * .4, er * .62), (0, -er * .42, 0), 'black', parent=e)
        part('sphere', (er * .17,) * 3, (-er * .2, -er * .78, er * .3), 'highlight', parent=e)
        b = piv['brow_' + side] = empty(f'{key_}_brow_{side}', head, (sx * f['ex'], f['ey'] - .01, f['ez'] + er * 1.45))
        part('sphere', (er * .85, .035, .03), (0, 0, 0), f.get('brow', 'dark'), parent=b)
    m = piv['mouth'] = empty(f'{key_}_mouth', head, (0, f['my'], f['mz']))
    part('sphere', (.085, .035, .05), (0, 0, 0), 'mouth', parent=m)
    m.scale[2] = 0.25
    return dict(root=root, piv=piv, eye_z=c['pivots']['head'][2] + f['ez'], brow_z=f['ez'] + er * 1.45)


# action = list of (pivot, path, index, [(frame offset | 'E'(+n) = line end, value)])
ARMS_UP = lambda keys: [('arm_l', 'rotation_euler', 1, keys), ('arm_r', 'rotation_euler', 1, keys)]
ACT = {
    'jump': [('body', 'location', 2, [(0, 0), (5, 0), (12, .7), (19, 0), (24, 0)]),
             ('body', 'scale', 2, [(0, 1), (5, .82), (10, 1.12), (19, .88), (24, 1)])] + ARMS_UP([(0, 0), (8, 1.2), (19, .3), (24, 0)]),
    'wave': [('arm_r', 'rotation_euler', 1, [(0, 0), (6, 2.5), (10, 2.1), (14, 2.6), (18, 2.1), (22, 2.6), (30, 0)]),
             ('head', 'rotation_euler', 1, [(0, 0), (8, .12), (30, 0)])],
    'nod': [('head', 'rotation_euler', 0, [(0, 0), (5, .25), (10, 0), (15, .25), (20, 0)])],
    'shake': [('head', 'rotation_euler', 2, [(0, 0), (5, .3), (10, -.3), (15, .3), (20, -.3), (25, 0)])],
    'spin': [],  # special-cased (cumulative rotation)
    'laugh': [('body', 'scale', 2, [(0, 1), (4, 1.07), (8, .96), (12, 1.07), (16, .96), (20, 1.07), (24, 1)]),
              ('head', 'rotation_euler', 0, [(0, 0), (4, -.2), (20, -.2), (26, 0)])],
    'shrug': ARMS_UP([(0, 0), (6, .8), (20, .8), (26, 0)]) + [('head', 'rotation_euler', 1, [(0, 0), (6, .18), (20, .18), (26, 0)]),
                                                               ('body', 'location', 2, [(0, 0), (6, .06), (20, .06), (26, 0)])],
    'point': [('arm_r', 'rotation_euler', 0, [(0, 0), (7, -1.5), (40, -1.5), (48, 0)]), ('arm_r', 'rotation_euler', 1, [(0, 0), (7, .3), (40, .3), (48, 0)])],
    'think': [('head', 'rotation_euler', 1, [(0, 0), (8, .22), (48, .22), (56, 0)]), ('head', 'rotation_euler', 0, [(0, 0), (8, -.12), (48, -.12), (56, 0)]),
              ('arm_r', 'rotation_euler', 0, [(0, 0), (8, -1.3), (48, -1.3), (56, 0)]), ('arm_r', 'rotation_euler', 1, [(0, 0), (8, -.5), (48, -.5), (56, 0)])],
    'dance': [('body', 'location', 0, [(0, 0), (6, .2), (12, -.2), (18, .2), (24, -.2), (30, .2), (36, -.2), (42, 0)]),
              ('body', 'rotation_euler', 1, [(0, 0), (6, .15), (12, -.15), (18, .15), (24, -.15), (30, .15), (36, -.15), (42, 0)])]
             + ARMS_UP([(0, 0), (6, 2.2), (12, .8), (18, 2.2), (24, .8), (30, 2.2), (36, .8), (42, 0)]),
    'sad': [('head', 'rotation_euler', 0, [(0, 0), (10, .35), ('E', .35), ('E10', 0)]), ('body', 'scale', 2, [(0, 1), (10, .94), ('E', .94), ('E10', 1)])],
    'surprised': [('body', 'location', 2, [(0, 0), (4, .3), (9, 0)]), ('body', 'scale', 2, [(0, 1), (4, 1.12), (9, .95), (13, 1)]),
                  ('head', 'rotation_euler', 0, [(0, 0), (5, -.15), (28, -.15), (36, 0)])] + ARMS_UP([(0, 0), (5, 1.4), (28, 1.4), (36, 0)]),
    'cheer': ARMS_UP([(0, 0), (6, 2.7), (30, 2.7), (38, 0)]) + [('body', 'location', 2, [(0, 0), (6, 0), (12, .5), (18, 0), (24, .5), (30, 0)]),
                                                                ('body', 'scale', 2, [(0, 1), (5, .88), (10, 1.08), (18, .92), (22, 1.08), (30, 1)])],
}
SPIN = {}


def do_action(ch, name, f0, f1, avail):
    C = CH[ch]
    if name == 'spin':
        b = SPIN.get(ch, 0.0); n = min(22, max(avail, 8))
        key(C['piv']['body'], 'rotation_euler', 2, f0, b); key(C['piv']['body'], 'rotation_euler', 2, f0 + n, b + math.tau)
        SPIN[ch] = b + math.tau
        return
    off = lambda d: d if isinstance(d, int) else (f1 - f0) + int(d[1:] or 0)
    length = max(off(d) for *_, ks in ACT[name] for d, _ in ks)
    s = min(1.0, avail / max(length, 1))  # squeeze if the next action comes sooner
    for pv, path, idx, ks in ACT[name]:
        sign = -1 if pv == 'arm_r' and idx == 1 else 1
        for d, v in ks: key(C['piv'][pv], path, idx, f0 + round(off(d) * s), v * sign)


def set_emotion(ch, emo, f):
    C = CH[ch]
    if C.get('emo') == emo: return
    for e, at in ((C.get('emo', 'neutral'), f), (emo, f + 5)):
        dz, tilt, mw = EMOTIONS[e]
        for side, sgn in (('l', -1), ('r', 1)):
            b = C['piv']['brow_' + side]
            key(b, 'location', 2, at, C['brow_z'] + dz); key(b, 'rotation_euler', 1, at, tilt * sgn)
        key(C['piv']['mouth'], 'scale', 0, at, mw)
    C['emo'] = emo


def turn(ch, th, f):
    C = CH[ch]
    if abs(C.get('th', 0) - th) < 1e-3: return
    key(C['root'], 'rotation_euler', 2, f, C.get('th', 0)); key(C['root'], 'rotation_euler', 2, f + 6, th)
    C['th'] = th


# ---------- build ----------
SCENES = EP['scenes']
CH = {c: build_char(c) for c in sorted({c for s in SCENES for c in s['characters']})}
for k, s in enumerate(SCENES): build_set(k, s)
build_sky()

POS = []
for k, s in enumerate(SCENES):
    n = len(s['characters'])
    POS.append({c: (k * GAP + (i - (n - 1) / 2) * 1.7, 0.15 * abs(i - (n - 1) / 2) ** 2, 0) for i, c in enumerate(s['characters'])})
    for c, C in CH.items():
        key(C['root'], 'location', None, TL['scenes'][k]['start'], POS[k].get(c, (0, 0, -500)), 'CONSTANT')

for c, C in CH.items():  # neutral keys before frame 1 so idle-noise curves exist
    b, h = C['piv']['body'], C['piv']['head']
    for ob, path, idx, v in ((b, 'rotation_euler', 1, 0), (b, 'scale', 2, 1), (h, 'rotation_euler', 0, 0), (h, 'rotation_euler', 2, 0)):
        key(ob, path, idx, 0, v)
    rng = random.Random(c)
    f = rng.randint(30, 90)
    while f < TL['frames']:
        for side in 'lr':
            e = C['piv']['eye_' + side]
            key(e, 'scale', 2, f - 1, 1); key(e, 'scale', 2, f + 1, .1); key(e, 'scale', 2, f + 3, 1)
        f += rng.randint(60, 140)

# when does each character next start an action? (to squeeze long actions)
acts = sorted((L['start'], c) for L in TL['lines'] for c in CH
              if (SCENES[L['scene']]['lines'][L['idx']]['who'] == c and SCENES[L['scene']]['lines'][L['idx']].get('action'))
              or (SCENES[L['scene']]['lines'][L['idx']].get('everyone') and c in SCENES[L['scene']]['characters']))
def next_act(c, f): return next((s for s, cc in acts if cc == c and s > f), TL['frames'])

cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); SC.collection.objects.link(cam); SC.camera = cam
tgt, focus = empty('cam_target'), empty('focus')
con = cam.constraints.new('TRACK_TO'); con.target, con.track_axis, con.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
cam.data.dof.use_dof = True; cam.data.dof.focus_object = focus
CUTS, shot_n = set(), 0
title = None

for i, L in enumerate(TL['lines']):
    k, s = L['scene'], SCENES[L['scene']]
    ln = s['lines'][L['idx']]; who, f0, f1 = ln['who'], L['start'], L['end']
    f_end = TL['lines'][i + 1]['start'] - 1 if i + 1 < len(TL['lines']) else TL['frames']
    ox, chars, pos = k * GAP, s['characters'], POS[k]
    if who != 'narrator':
        m = CH[who]['piv']['mouth']
        key(m, 'scale', 2, f0 - 1, .25, 'LINEAR')
        for j, a in enumerate(L['mouth'][::2]): key(m, 'scale', 2, f0 + 2 * j, .25 + 1.5 * a)
        key(m, 'scale', 2, f1 + 1, .25)
    for c in chars:
        set_emotion(c, ln.get('emotion', 'neutral') if c == who or ln.get('everyone') else 'neutral', f0)
        x = pos[c][0]
        if who == 'narrator': th = 0
        elif c == who: th = -0.18 * math.copysign(1, x - ox) if abs(x - ox) > .1 else 0
        else: th = 0.45 * math.copysign(1, pos[who][0] - x)
        turn(c, th, f0)
    if ln.get('action') and who != 'narrator': do_action(who, ln['action'], f0, f1, next_act(who, f0) - f0)
    if ln.get('everyone'):
        for c in chars:
            if not (c == who and ln.get('action')): do_action(c, ln['everyone'], f0, f1, next_act(c, f0) - f0)
    # camera
    first = L['idx'] == 0
    if first:
        c0, c1, t0, t1, lens, fs, fp = (ox - 3, -15, 4.6), (ox - 1, -12.5, 3.6), (ox, 3, 2.2), (ox, 0, 1.3), 30, 16, (ox, 0, 1)
    elif who == 'narrator' or ln.get('everyone'):
        a = 1 if shot_n % 2 else -1
        c0, c1, t0, t1, lens, fs, fp = (ox + a * 1.8, -10.5, 2.9), (ox + a * 1.2, -9.8, 2.7), (ox, 0, 1.15), (ox, 0, 1.15), 35, 11, (ox, 0, 1)
    else:
        sx, ez = pos[who][0], CH[who]['eye_z']
        side = math.copysign(1, sx - ox) if abs(sx - ox) > .1 else 1
        if shot_n % 2:
            c0, c1, t0, lens, fs = (sx - side * .6, -4.6, ez + .2), (sx - side * .5, -4.3, ez + .18), (sx, 0, ez - .12), 45, 2.8
        else:
            c0, c1, t0, lens, fs = (sx - side * 1.1, -7.2, ez + .5), (sx - side * .9, -6.6, ez + .45), (sx, 0, ez - .3), 38, 4
        t1, fp = t0, (sx, -0.3, ez)
    shot_n += 1
    key(cam, 'location', None, f0, c0); key(cam, 'location', None, f_end, c1)
    key(tgt, 'location', None, f0, t0); key(tgt, 'location', None, f_end, t1)
    key(focus, 'location', None, f0, fp, 'CONSTANT')
    cam.data.lens, cam.data.dof.aperture_fstop = lens, fs
    cam.data.keyframe_insert('lens', frame=f0); cam.data.keyframe_insert('dof.aperture_fstop', frame=f0)
    CUTS.add(f_end)
    if i == 0:  # episode title pops in over the opening shot
        cu = bpy.data.curves.new('title', 'FONT'); cu.body = EP['title'].split('|')[0].strip()
        cu.font = bpy.data.fonts.load(FONT); cu.size, cu.extrude, cu.bevel_depth = 0.8, 0.08, 0.02
        cu.align_x, cu.align_y = 'CENTER', 'CENTER'; cu.text_boxes[0].width, cu.text_boxes[0].x = 8, -4
        title = bpy.data.objects.new('title', cu); SC.collection.objects.link(title)
        title.data.materials.append(mat('gold'))
        title.location, title.rotation_euler = (ox - 1.7, -7.5, 3.9), (math.radians(78), 0, math.radians(-8))
        for fr, v in ((1, 0), (f0, 0), (f0 + 8, 1.15), (f0 + 12, 1), (f_end - 8, 1), (f_end, 0)): key(title, 'scale', None, fr, (v,) * 3)

# interpolation + idle life (noise = strength, period in frames)
NOISE = {('_body', 'rotation_euler', 1): (.06, 45), ('_body', 'scale', 2): (.03, 30),
         ('_head', 'rotation_euler', 0): (.08, 55), ('_head', 'rotation_euler', 2): (.12, 70)}
for ob in bpy.data.objects:
    if not ob.animation_data or not ob.animation_data.action: continue
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = ('CONSTANT' if kp.co.x in CUTS else 'LINEAR') if ob in (cam, tgt) else INTERP.get((ob.name, fc.data_path), 'BEZIER')
        nz = NOISE.get((ob.name[ob.name.rfind('_'):], fc.data_path, fc.array_index))
        if nz:
            mod = fc.modifiers.new('NOISE'); mod.strength, mod.scale, mod.phase = *nz, random.Random(ob.name).uniform(0, 100)
for fc in cam.data.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# ---------- render ----------
SC.render.engine = 'CYCLES'; SC.cycles.device = 'CPU'
SC.cycles.samples = int(os.environ.get('SAMPLES', 24))
SC.cycles.use_adaptive_sampling, SC.cycles.adaptive_threshold = True, 0.04
SC.cycles.use_denoising, SC.cycles.denoiser = True, 'OPENIMAGEDENOISE'
SC.cycles.max_bounces, SC.cycles.diffuse_bounces, SC.cycles.glossy_bounces = 2, 1, 1
SC.cycles.transmission_bounces = SC.cycles.volume_bounces = SC.cycles.transparent_max_bounces = 0
SC.cycles.use_fast_gi, SC.cycles.fast_gi_method = True, 'REPLACE'
SC.world.light_settings.ao_factor, SC.world.light_settings.distance = 1.0, 3.0
SC.cycles.caustics_reflective = SC.cycles.caustics_refractive = False
SC.cycles.sample_clamp_indirect = 4
SC.render.use_persistent_data = True
SC.render.resolution_x, SC.render.resolution_y = map(int, os.environ.get('RES', '1920x1080').split('x'))
SC.render.resolution_percentage, SC.render.fps = 100, FPS
SC.view_settings.view_transform = 'Standard'  # vivid cartoon colours (AgX looked washed out)

if MODE == 'thumb':
    sl, li = EP.get('thumbnail_line', [0, 0])
    L = next(l for l in TL['lines'] if l['scene'] == sl and l['idx'] == li)
    SC.frame_set(L['start'] + 14)
    SC.render.resolution_x, SC.render.resolution_y, SC.cycles.samples = 1280, 720, 64
    SC.render.image_settings.file_format = 'PNG'; SC.render.filepath = f'{OUT}/thumb.png'
    bpy.ops.render.render(write_still=True)
elif MODE.startswith('preview:'):
    SC.render.image_settings.file_format = 'JPEG'
    for fr in map(int, MODE[8:].split(',')):
        SC.frame_set(fr); SC.render.filepath = f'{OUT}/preview_{fr:05d}.jpg'; bpy.ops.render.render(write_still=True)
else:
    n = int(MODE); SC.frame_start, SC.frame_end = TL['chunks'][n]
    r = SC.render; r.image_settings.file_format = 'FFMPEG'
    r.ffmpeg.format, r.ffmpeg.codec, r.ffmpeg.constant_rate_factor, r.ffmpeg.ffmpeg_preset = 'MPEG4', 'H264', 'PERC_LOSSLESS', 'GOOD'
    r.ffmpeg.gopsize, r.ffmpeg.audio_codec = FPS, 'NONE'
    r.filepath = f'{OUT}/chunk_{n:03d}_'
    bpy.ops.render.render(animation=True)
