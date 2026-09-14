#!/usr/bin/env python3
"""Work out what goes where from the device map, instead of a hand-written list.

The first version of this wizard carried a table of `(device, button, action)`
written from memory of the hardware, and got it wrong twice: countermeasures
landed on a hat direction because a DCS command called "Paddle Switch" was read
as a description of the paddle, and flaps were split across what turned out to
be one hat.

Now the hardware describes itself. ../sim-device-map knows the SHAPE of every
control -- a four-way hat, a three-stage cumulative trigger, a sprung two-way
hat, a thumb-reachable paddle -- and each need below says what shape it wants.
Matching the two is the whole job, and the reasoning prints with `--why`.

    ./plan.py            # the assignment, grouped by device
    ./plan.py --why      # and why each control was chosen
    ./plan.py --unused   # what is still free
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
#: the shared hardware map. Sibling directory by default; SIM_DEVICE_MAP
#: overrides it, for a clone that does not sit next to this one.
MAP = os.environ.get('SIM_DEVICE_MAP') or os.path.normpath(
    os.path.join(HERE, '..', 'sim-device-map'))
if not os.path.isdir(MAP):
    raise SystemExit(
        f'no device map at {MAP}\n'
        'clone sim-device-map next to this repo, or set SIM_DEVICE_MAP')
if MAP not in sys.path:
    sys.path.insert(0, MAP)

import devicemap                                        # noqa: E402

def _built(name, key):
    path = os.path.join(HERE, name)
    try:
        return json.load(open(path, encoding='utf-8'))[key]
    except OSError:
        sys.exit(f'{name} is missing -- it is built from the installed game,\n'
                 f'not kept in the repo. Run ./harvest.py')


ACTIONS = _built('wt-actions.json', 'actions')
try:
    FACTORY = dict(_built('wt-factory-rank.json', 'actions'))
except SystemExit:
    FACTORY = {}          # only used to annotate --why, so it may be absent


def is_heli(action):
    """War Thunder is not consistent: most helicopter actions carry
    `_HELICOPTER` as a suffix, but a handful wear it as a prefix
    (`ID_HELICOPTER_TRIM`). Getting this wrong puts two actions on one button
    in the same context and the game drops one of them."""
    return action.endswith('_HELICOPTER') or action.startswith('ID_HELICOPTER')


def contexts(action):
    """Which vehicle contexts an action actually applies to.

    The trap: War Thunder names most helicopter actions with an `_HELICOPTER`
    suffix and a few with an `ID_HELICOPTER_` prefix, so a twin has to be
    looked for in BOTH forms. And an action with no twin in either form is
    SHARED -- it applies to helicopters as well as aircraft, whatever we meant
    by putting it there. `ID_TRIM_ELEVATOR_MINUS` has no helicopter twin, so it
    is live in a helicopter too.
    """
    if is_heli(action):
        return ('heli',)
    twins = (action + '_HELICOPTER', action.replace('ID_', 'ID_HELICOPTER_', 1))
    if any(t in ACTIONS for t in twins):
        return ('air',)
    return ('air', 'heli')


class Need:
    """One thing a pilot has to be able to do, and the shape it wants.

    `air` and `heli` are action ids in the order the control's own directions
    or stages run, so a four-way hat takes four and a trigger takes one per
    detent.
    """

    def __init__(self, what, shape, air=(), heli=(), push=None, heli_push=None,
                 suits=None, reflex=False, device=None, note=''):
        self.what = what
        self.shape = shape if isinstance(shape, tuple) else (shape,)
        self.air = list(air)
        self.heli = list(heli)
        self.push = push
        self.heli_push = heli_push
        self.suits = suits
        self.reflex = reflex
        self.device = device
        self.note = note

    @property
    def slots(self):
        return max(len(self.air), len(self.heli))


# Ordered by what you lose first if it is missing. The matcher works down the
# list, so the earliest needs get the best control that fits them.
NEEDS = [
    Need('Guns', 'trigger',
         air=['ID_FIRE_MGUNS', 'ID_FIRE_CANNONS', 'ID_FIRE_ADDITIONAL_GUNS'],
         heli=['ID_FIRE_MGUNS_HELICOPTER', 'ID_FIRE_CANNONS_HELICOPTER',
               'ID_FIRE_ADDITIONAL_GUNS_HELICOPTER'],
         note='cumulative stages: pulling through fires everything up to it'),

    Need('Countermeasures', ('paddle', 'button'), air=['ID_FLARES'],
         heli=['ID_FLARES_HELICOPTER'], suits='reflex', reflex=True,
         note='has to be reachable mid-manoeuvre without regripping'),

    Need('Fire missile', 'button', air=['ID_AAM'], heli=['ID_ATGM_HELICOPTER'],
         suits='fire', reflex=True, device='stick'),

    Need('Fire rockets', 'button', air=['ID_ROCKETS'],
         heli=['ID_ROCKETS_HELICOPTER'], suits='fire', reflex=True,
         device='stick'),

    Need('Views', 'hat4',
         air=['ID_CAMERA_DEFAULT', '', 'ID_CAMERA_VIEW_DOWN',
              'ID_CAMERA_VIEW_BACK'],
         heli=['ID_CAMERA_DEFAULT', 'ID_CAMERA_GUNNER_HELICOPTER',
               'ID_CAMERA_VIEW_DOWN', 'ID_CAMERA_VIEW_BACK'],
         push='ID_CAMERA_NEUTRAL', suits='view', reflex=True, device='stick',
         note='look back matters more in a dogfight than anything else here'),

    Need('Radar / IRST', 'hat4',
         air=['ID_SENSOR_SWITCH', 'ID_SENSOR_RANGE_SWITCH',
              'ID_SENSOR_MODE_SWITCH', 'ID_SENSOR_TARGET_SWITCH'],
         heli=['ID_SENSOR_SWITCH_HELICOPTER', 'ID_SENSOR_RANGE_SWITCH_HELICOPTER',
               'ID_SENSOR_MODE_SWITCH_HELICOPTER',
               'ID_SENSOR_TARGET_SWITCH_HELICOPTER'],
         push='ID_SENSOR_TARGET_LOCK', heli_push='ID_SENSOR_TARGET_LOCK_HELICOPTER',
         suits='sensor', reflex=True, device='stick'),

    Need('Weapon lock', 'button', air=['ID_WEAPON_LOCK'],
         heli=['ID_WEAPON_LOCK_HELICOPTER'], suits='lock', reflex=True,
         device='stick', note='the seeker lock you hold while a heater growls'),

    Need('Trim', 'hat4',
         air=['ID_TRIM_ELEVATOR_PLUS', 'ID_TRIM_AILERONS_PLUS',
              'ID_TRIM_ELEVATOR_MINUS', 'ID_TRIM_AILERONS_MINUS'],
         heli=(),
         push='ID_TRIM', heli_push='ID_HELICOPTER_TRIM', suits='trim',
         reflex=True, device='stick',
         note='hat trim is the DCS habit; ID_TRIM on the push is the WT idiom'),

    Need('WEP / afterburner', 'button', air=['ID_IGNITE_BOOSTERS'],
         suits='reflex', reflex=True, device='throttle'),


    Need('Radar ACM', 'button', air=['ID_SENSOR_ACM_SWITCH'], suits='sensor',
         reflex=True, note='short-range auto-acquire; matters from the 1970s on'),


    Need('Sight stabilization', 'button',
         heli=['ID_LOCK_TARGETING_AT_POINT_HELICOPTER'], suits='lock',
         reflex=True, note='the core of the ATGM workflow'),


    Need('Bombs', 'button', air=['ID_BOMBS'], heli=['ID_BOMBS_HELICOPTER'],
         suits='release', reflex=True),

    Need('Air-to-ground lock', 'button', air=['ID_AGM_LOCK'],
         heli=['ID_AGM_LOCK_HELICOPTER'], suits='lock', reflex=True),

    Need('Gear', ('hat2', 'switch2'), air=['ID_GEAR', 'ID_GEAR'],
         heli=['ID_GEAR_HELICOPTER', 'ID_GEAR_HELICOPTER'], suits='toggle',
         note='a toggle on both ends, so the lever position matches the gear'),

    Need('Flaps', 'hat2', air=['ID_FLAPS_UP', 'ID_FLAPS_DOWN'],
         suits='stepped-pair',
         note='WT steps through combat, takeoff and landing settings'),

    Need('Airbrake', 'button', air=['ID_AIR_BRAKE'], suits='toggle',
         reflex=True),

        Need('Hover mode', 'button', heli=['ID_CONTROL_MODE_HELICOPTER'],
         suits='toggle'),

    Need('SAS', 'button', heli=['ID_FBW_MODE_HELICOPTER'], suits='toggle'),

        Need('Cockpit / external view', 'hat2',
         air=['ID_CAMERA_FPS', 'ID_CAMERA_TPS'],
         heli=['ID_CAMERA_FPS_HELICOPTER', 'ID_CAMERA_TPS_HELICOPTER'],
         suits='view'),

        Need('Radar / IRST swap', 'button', air=['ID_SENSOR_TYPE_SWITCH'],
         suits='sensor'),

    Need('Engine', 'button', air=['ID_TOGGLE_ENGINE'],
         heli=['ID_TOGGLE_ENGINE_HELICOPTER'], suits='occasional'),

    Need('Tactical map', 'button', air=['ID_TACTICAL_MAP'], suits='occasional',
         note='the only navigation there is in simulator battles'),

    Need('Bomb bay', 'button', air=['ID_BAY_DOOR'], suits='occasional'),

    Need('Drag chute', 'button', air=['ID_CHUTE'], suits='occasional'),

    Need('Laser designator', 'button',
         heli=['ID_TOGGLE_LASER_DESIGNATOR_HELICOPTER'], suits='occasional'),

    Need('Weapon select', 'hat2',
         heli=['ID_SWITCH_SHOOTING_CYCLE_PRIMARY_HELICOPTER',
               'ID_SWITCH_SHOOTING_CYCLE_SECONDARY_HELICOPTER'],
         suits='stepped-pair'),
]

# name in WT, the control kind it belongs on, and which of its axes
AXIS_NEEDS = [
    ('ailerons',                'stick-x',      False),
    ('elevator',                'stick-y',      True),
    ('rudder',                  'twist',        False),
    ('helicopter_cyclic_roll',  'stick-x',      False),
    ('helicopter_cyclic_pitch', 'stick-y',      True),
    ('helicopter_pedals',       'twist',        False),
    ('throttle',                'throttle-lever', False),
    ('helicopter_collective',   'throttle-lever', False),
    ('camx',                    'view-x',       False),
    ('camy',                    'view-y',       False),
    ('helicopter_camx',         'view-x',       False),
    ('helicopter_camy',         'view-y',       False),
    ('sensor_cue_x',            'cue-x',        False),
    ('sensor_cue_y',            'cue-y',        False),
    ('helicopter_atgm_aim_x',   'cue-x',        False),
    ('helicopter_atgm_aim_y',   'cue-y',        False),
    ('brake_left',              'brake',        False),
    ('brake_right',             'brake',        False),
    ('zoom',                    'zoom',         False),
]


#: Extra deadzone for a named axis, overriding the rule in build().
#
# The stick twist is the rudder, and in War Thunder that is a problem no other
# sim of the four has. Hauling the stick back while rolling rotates the
# forearm, so yaw creeps in on its own -- and WT is the one that wants reflex
# shooting, which is when it happens. DCS and MSFS are flown deliberately and
# never showed it, so this stays local to this repo rather than becoming a
# device-map fact.
#
# Only `rudder` widens. `helicopter_pedals` is the SAME physical axis but not
# the same kind of control: heli yaw is held continuously and a wide dead patch
# makes a hover harder, where a plane's rudder is tapped.
#
# WT's own `nonlinearity: 2.5` already softens the centre, so the felt dead
# region is wider than the number. The other half of this -- capping authority
# with `rudderMultiplier` -- lives OUTSIDE the controls{} block that
# wt-bind-preset.py rewrites, so it is a slider in the game's own UI, not ours.
#
# A stopgap: VIRPIL pedals are on order. Delete this when they arrive.
AXIS_DEADZONE = {'rudder': 0.10}

#: Axis properties the plan wants to OWN, overriding whatever the game's own
#: axis wizard left in the file. Everything not named here is still preserved,
#: because that wizard knows about calibration and we do not.
#
# zoom kMul: the dial is not sprung -- it stays where you leave it, and it was
# measured resting at 27535 of 32767, deep in the top of its travel. `kMul: 2`
# doubles the gain, so the output is already clamped at full zoom across the
# whole upper half of the dial. Nothing happens until you wind back past the
# middle, which is exactly the "I have to turn it a long way before it lets go"
# that shows up when the sight view sets its own zoom. At 1 the whole dial maps
# to the whole range with no plateau.
AXIS_PROPS = {
    'zoom': {'kMul': 1.0},
}


def devices():
    out = {}
    for d in devicemap.load_all():
        out[d.kind] = d
    missing = {'stick', 'throttle'} - set(out)
    if missing:
        sys.exit(f'device map has no {", ".join(sorted(missing))} -- '
                 f'capture one in {MAP}')
    return out


def score(ctrl, need, role):
    """How well a control fits a need. None means it cannot."""
    if ctrl.kind not in need.shape:
        return None
    if len(ctrl.bindable_buttons) < need.slots:
        return None
    regrip = ctrl.reach == 'needs letting go'
    if need.reflex and regrip:
        return None                    # no use if you must let go to reach it
    s = 100
    if need.suits and need.suits in ctrl.suits:
        s += 40
    if need.device == role:
        s += 30
    elif need.device and need.device != role:
        s -= 40
    if not regrip:
        s += 15
    if ctrl.kind == need.shape[0]:
        s += 10                        # the shape asked for first
    # a hat with a push is worth more to a need that has something for it
    if need.push and ctrl.push is not None:
        s += 10
    # do not spend a five-slot hat on a two-slot need
    s -= 3 * (len(ctrl.bindable_buttons) - need.slots)
    return s


def assign():
    devs = devices()
    pool = [(role, c) for role, d in devs.items()
            for c in d.groups(bindable=True)]
    taken, out, unmet = set(), [], []

    for need in NEEDS:
        best, best_s = None, None
        for i, (role, c) in enumerate(pool):
            if i in taken:
                continue
            s = score(c, need, role)
            if s is not None and (best_s is None or s > best_s):
                best, best_s = i, s
        if best is None:
            unmet.append(need)
            continue
        taken.add(best)
        role, c = pool[best]
        out.append((need, role, c, best_s))
    # A hat carries its directions AND a press; if the need that took it had
    # nothing for the press, that press is still a button somebody can use.
    spoken_for = {id(c) for _, _, c, _ in out if _push_used(out, c)}
    still = []
    for need in unmet:
        if need.slots != 1:
            still.append(need)
            continue
        best, best_s = None, None
        for i, (role, c) in enumerate(pool):
            if c.push is None or id(c) in spoken_for:
                continue
            if i in taken and _push_used(out, c):
                continue
            s_ = score_push(c, need, role)
            if s_ is not None and (best_s is None or s_ > best_s):
                best, best_s = (role, c), s_
        if best is None:
            still.append(need)
            continue
        role, c = best
        spoken_for.add(id(c))
        out.append((need, role, c, best_s))
    unmet = still
    used_axes = set()
    for _, want, _ in AXIS_NEEDS:
        r, a = axis_of(devs, want)
        if a is not None:
            used_axes.add((r, a.index))
    free = []
    for i, (r, c) in enumerate(pool):
        if i in taken or id(c) in spoken_for:
            continue
        if c.axes and any((r, x) in used_axes for x in c.axes):
            continue                    # its axes are carrying something
        free.append((r, c))
    return devs, out, unmet, free


def _push_used(out, ctrl):
    return any(c is ctrl and (n.push or n.heli_push) for n, _, c, _ in out)


def score_push(ctrl, need, role):
    """Scoring a bare press, borrowed from a control whose need left it idle."""
    if ctrl.push is None:
        return None
    if need.reflex and ctrl.reach == 'needs letting go':
        return None
    s = 60
    if need.suits and need.suits in ctrl.suits:
        s += 30
    if need.device == role:
        s += 30
    if ctrl.reach != 'needs letting go':
        s += 15
    return s


def axis_of(devs, want):
    """Find the axis a need names, by what the map says it is."""
    stick, thr = devs['stick'], devs['throttle']
    def by_kind(dev, kind):
        return next((a for a in dev.axes() if a.kind == kind), None)
    if want == 'stick-x':
        return 'stick', by_kind(stick, 'stick-x')
    if want == 'stick-y':
        return 'stick', by_kind(stick, 'stick-y')
    if want == 'twist':
        return 'stick', by_kind(stick, 'twist')
    if want == 'throttle-lever':
        a = next((x for x in thr.axes()
                  if x.kind == 'lever' and 'left' in (x.label or '').lower()), None)
        return 'throttle', a or by_kind(thr, 'lever')
    if want in ('view-x', 'view-y'):
        g = next((g for g in thr.groups('ministick')), None)
        if not g or len(g.axes) < 2:
            return 'throttle', None
        return 'throttle', thr.axis(g.axes[0 if want == 'view-x' else 1])
    if want in ('cue-x', 'cue-y'):
        g = next((g for g in stick.groups('ministick')), None)
        if not g or len(g.axes) < 2:
            return 'stick', None
        return 'stick', stick.axis(g.axes[0 if want == 'cue-x' else 1])
    if want == 'brake':
        return 'stick', next((a for a in stick.axes()
                              if a.kind in ('slider', 'lever')
                              and a.safe_for_absolute), None)
    if want == 'zoom':
        # A dial first, to match DCS: the same hand does the same thing in both
        # sims, which is worth more than either sim's local optimum. It rests
        # centred rather than at zero, so the view starts part-zoomed -- live
        # with it, or fall back to a slider that rests at its minimum.
        dial = next((a for a in thr.axes(kind='dial') if a.proportional), None)
        if dial:
            return 'throttle', dial
        return 'throttle', next((a for a in thr.axes()
                                 if a.kind == 'slider'
                                 and a.safe_for_absolute
                                 and a.proportional), None)
    return None, None


def build():
    """The tables wt-bind-preset.py consumes: (name, role, idx, inverse, props)
    and (role, idx, action, where)."""
    devs, chosen, unmet, free = assign()
    axes, buttons = [], []

    for name, want, inverse in AXIS_NEEDS:
        role, a = axis_of(devs, want)
        if a is None:
            continue
        dead = AXIS_DEADZONE.get(name)
        if dead is None:
            dead = 0.06 if a.kind.startswith('mini-stick') else (
                0 if a.kind == 'lever' else 0.02)
        props = {'innerDeadzone': dead}
        props.update(AXIS_PROPS.get(name, {}))
        axes.append((name, role, a.index, inverse, props))

    placed, emitted = [], set()
    for need, role, c, _ in chosen:
        seq = c.bindable_buttons
        order = [b for b in c.buttons if b in seq] or seq
        if need.slots == 1 and not need.push and c.push is not None \
                and len(order) > 1:
            order = [c.push]            # it was given the press, not the hat
        used = list(order[:need.slots])
        if need.push and c.push is not None:
            used.append(c.push)
        placed.append((need, role, c, used))
        for ctx, ids, pushid in (('air', need.air, need.push),
                                 ('heli', need.heli, need.heli_push or need.push)):
            for i, action in enumerate(ids):
                if not action or i >= len(order):
                    continue
                key = (role, order[i], action)
                if key in emitted:
                    continue            # shared actions sit in both lists
                emitted.add(key)
                buttons.append((role, order[i], action,
                                f'{c.label} — {c.direction(order[i]) or "press"}'))
            if pushid and c.push is not None and (role, c.push, pushid) not in emitted:
                emitted.add((role, c.push, pushid))
                buttons.append((role, c.push, pushid, f'{c.label} — push'))

    # No button may carry two different actions in one context: the game
    # silently drops one of them, and which one is not worth relying on.
    #
    # This is stricter than it looks. An aircraft action with no helicopter
    # twin is live in helicopters too, so pairing it with a helicopter-specific
    # action on the same slot clashes even though the two names look unrelated
    # -- which is how the views hat ended up with the bomb sight fighting the
    # gunner view, and the trim hat with elevator trim fighting trim reset.
    #
    # That is a mistake in NEEDS, not something to paper over at write time,
    # so it stops here rather than warning.
    seen, clashes = {}, []
    for role, idx, action, where in buttons:
        for ctx in contexts(action):
            key = (role, idx, ctx)
            if key in seen and seen[key] != action:
                clashes.append(f'{role} button {idx} ({ctx}): '
                               f'{seen[key]} and {action}   [{where}]')
            seen[key] = action
    if clashes:
        for c in clashes:
            print(f'!! {c}', file=sys.stderr)
        sys.exit('refusing to plan: those two would share a button in one '
                 'vehicle context and the game keeps only one. Fix NEEDS.')
    return axes, buttons, placed, unmet, free


def wt_offsets():
    """War Thunder numbers buttons and axes globally across devices, in the
    order they appear in machine.blk. The sheet has to print the number you
    will actually see in the menu, not the local one."""
    import glob
    import re
    out = {}
    for path in glob.glob(os.path.expanduser(
            '~/.config/WarThunder/Saves/last/production/machine.blk')):
        txt = open(path, encoding='utf-8', errors='replace').read()
        m = re.search(r'deviceMapping\{(.*?)\n    \}', txt, re.S)
        if not m:
            continue
        for blk in re.findall(r'joystick\{(.*?)\}', m.group(1), re.S):
            d = dict(re.findall(r'(\w+):[a-z]=("?[^"\n]*"?)', blk))
            name = d.get('name', '').strip('"').lower()
            role = 'throttle' if 'throttle' in name else 'stick'
            out[role] = (int(d.get('axesOffset', 0)),
                         int(d.get('buttonsOffset', 0)))
    return out or {'throttle': (0, 0), 'stick': (7, 51)}


def en(action):
    return ACTIONS.get(action, (action, ''))[0]


def sheet(path):
    axes, buttons, placed, unmet, free = build()
    off = wt_offsets()
    devs = devices()

    per = {}
    for role, idx, action, where in buttons:
        cell = per.setdefault((role, idx), {'where': where, 'air': [], 'heli': []})
        if is_heli(action):
            where_to = ['heli']
        elif action + '_HELICOPTER' in ACTIONS:
            where_to = ['air']          # the game ships a separate heli twin
        else:
            where_to = ['air', 'heli']  # no twin: it works in both
        for k in where_to:
            if action not in cell[k]:
                cell[k].append(action)

    L = ['# Kneeboard — War Thunder',
         '',
         'What sits under which finger, for air Simulator Battles and',
         'helicopters. Action names are as they appear in the game menu.',
         '',
         '**Generated** by `./plan.py --sheet` from `../sim-device-map` and the',
         "game's own action list. Do not edit by hand -- recapture the hardware",
         'or change `NEEDS` in `plan.py` and run it again.',
         '',
         'War Thunder numbers buttons globally across devices, so the **WT**',
         'column is what the menu shows: device offset plus the local number.',
         '']

    for role in ('stick', 'throttle'):
        d = devs[role]
        ax_off, btn_off = off.get(role, (0, 0))
        L += [f'## {d.product}', '',
              f'Buttons {btn_off}–{btn_off + d.n_buttons - 1}, '
              f'axes {ax_off}–{ax_off + d.n_axes - 1}', '',
              '| Control | WT | Air | Helicopter |',
              '|---|---|---|---|']
        rows = [(idx, v) for (r, idx), v in per.items() if r == role]
        for idx, v in sorted(rows):
            g = d.group_of(idx)
            part = g.direction(idx) if g else ''
            name = f'{g.label}' if g else f'button {idx}'
            if part:
                name += f' — {part}'
            air = ' · '.join(en(a) for a in v['air']) or '—'
            heli = ' · '.join(en(a) for a in v['heli']) or '—'
            L.append(f'| {name} | `{btn_off + idx}` | {air} | {heli} |')
        L.append('')

    L += ['## Axes', '', '| Control | WT | Air | Helicopter |', '|---|---|---|---|']
    seen = {}
    for name, role, idx, inverse, _ in axes:
        seen.setdefault((role, idx), {'air': [], 'heli': [], 'inv': inverse})
        key = 'heli' if name.startswith('helicopter_') else 'air'
        seen[(role, idx)][key].append(name)
    for (role, idx), v in sorted(seen.items(), key=lambda x: (x[0][0], x[0][1])):
        d = devs[role]
        ax_off = off.get(role, (0, 0))[0]
        a = d.axis(idx)
        g = d.axis_group(idx)
        label = (g.label if g else (a.label if a else f'axis {idx}'))
        extra = ' *(inverted)*' if v['inv'] else ''
        L.append(f'| {label} | `{ax_off + idx}` | '
                 f'{" · ".join(v["air"]) or "—"} | '
                 f'{" · ".join(v["heli"]) or "—"} |{extra}')
    L.append('')

    if free:
        L += ['## Left free', '',
              'Nothing here is wasted by accident -- these had no need that',
              'wanted their shape.', '',
              '| Control | Buttons | Reach |', '|---|---|---|']
        for role, c in free:
            btn_off = off.get(role, (0, 0))[1]
            ids = ', '.join(str(btn_off + b) for b in c.bindable_buttons) or '—'
            L.append(f'| {c.label} ({c.kind}) | {ids} | {c.reach} |')
        L.append('')

    if unmet:
        L += ['## Not placed', '']
        for n in unmet:
            L.append(f'- **{n.what}** — wanted a `{"/".join(n.shape)}`'
                     + (f' suiting `{n.suits}`' if n.suits else ''))
        L.append('')

    L += ['## Check in flight', '',
          '- **Elevator trim direction** — hat up should raise the nose.',
          '- **Zoom axis** — it rests at minimum, so the view should start',
          '  unzoomed. If not, invert it.',
          '- **View mini-stick** — your head should go where your thumb goes.',
          '',
          '## Undo', '',
          '```',
          './wt-bind-preset.py --restore',
          '```',
          '',
          'The game must be closed: it rewrites `machine.blk` on exit.', '']

    open(path, 'w', encoding='utf-8').write('\n'.join(L))
    return path, len(buttons), len(axes)


def _esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;'))


def html_sheet(path):
    """The same data as --sheet, laid out in columns to sit open on a second
    screen. Generated, so it cannot drift from what is actually bound."""
    import datetime
    axes, buttons, placed, unmet, free = build()
    off = wt_offsets()
    devs = devices()

    per = {}
    for role, idx, action, where in buttons:
        cell = per.setdefault((role, idx), {'air': [], 'heli': []})
        if is_heli(action):
            keys = ['heli']
        elif action + '_HELICOPTER' in ACTIONS:
            keys = ['air']
        else:
            keys = ['air', 'heli']
        for k in keys:
            if action not in cell[k]:
                cell[k].append(action)

    def device_panel(role):
        d = devs[role]
        ax_off, btn_off = off.get(role, (0, 0))
        rows = []
        for idx, v in sorted((i, c) for (r, i), c in per.items() if r == role):
            g = d.group_of(idx)
            part = g.direction(idx) if g else ''
            name = _esc(g.label if g else f'button {idx}')
            if part:
                name += f' <em>{_esc(part)}</em>'
            air = ' · '.join(_esc(en(a)) for a in v['air'])
            heli = ' · '.join(_esc(en(a)) for a in v['heli'])
            rows.append(
                f'<tr><td class="c">{name}</td><td class="n">{btn_off + idx}</td>'
                f'<td{"" if air else " class=\"none\""}>{air or "—"}</td>'
                f'<td class="h">{heli or "—"}</td></tr>')
        return (f'<div class="panel"><h2>{_esc(d.product)}'
                f'<small>buttons {btn_off}–{btn_off + d.n_buttons - 1}</small>'
                f'</h2><table><tr><th>Control</th><th>WT</th>'
                f'<th class="a">Air</th><th class="h">Helicopter</th></tr>'
                + ''.join(rows) + '</table></div>')

    seen = {}
    for name, role, idx, inverse, _ in axes:
        cell = seen.setdefault((role, idx), {'air': [], 'heli': [], 'inv': inverse})
        cell['heli' if name.startswith('helicopter_') else 'air'].append(name)
    arows = []
    for (role, idx), v in sorted(seen.items()):
        d = devs[role]
        ax_off = off.get(role, (0, 0))[0]
        a, g = d.axis(idx), d.axis_group(idx)
        label = _esc(g.label if g else (a.label if a else f'axis {idx}'))
        if v['inv']:
            label += ' <em>inverted</em>'
        arows.append(
            f'<tr><td class="c">{label}</td><td class="n">{ax_off + idx}</td>'
            f'<td>{" · ".join(_esc(x) for x in v["air"]) or "—"}</td>'
            f'<td class="h">{" · ".join(_esc(x) for x in v["heli"]) or "—"}</td>'
            f'</tr>')
    axes_panel = ('<div class="panel"><h2>Axes</h2><table>'
                  '<tr><th>Control</th><th>WT</th><th class="a">Air</th>'
                  '<th class="h">Helicopter</th></tr>'
                  + ''.join(arows) + '</table></div>')

    frows = []
    for role, c in free:
        btn_off = off.get(role, (0, 0))[1]
        ids = ', '.join(str(btn_off + b) for b in c.bindable_buttons) or '—'
        frows.append(f'<tr><td class="c">{_esc(c.label)}</td>'
                     f'<td class="n">{ids}</td>'
                     f'<td class="h">{_esc(c.reach)}</td></tr>')
    free_panel = ('<div class="panel"><h2>Left free<small>nothing here is'
                  ' wasted by accident</small></h2><table>'
                  '<tr><th>Control</th><th>WT</th><th>Reach</th></tr>'
                  + ''.join(frows) + '</table></div>')

    tpl = open(os.path.join(HERE, 'sheet-template.html'), encoding='utf-8').read()
    out = (tpl.replace('__STICK__', device_panel('stick'))
              .replace('__THROTTLE__', device_panel('throttle'))
              .replace('__AXES__', axes_panel)
              .replace('__FREE__', free_panel)
              .replace('__STAMP__', f'generated {datetime.date.today()} '
                                    f'· {len(buttons)} bindings ·'
                                    f' {len(axes)} axes'))
    open(path, 'w', encoding='utf-8').write(out)
    return path, len(buttons), len(axes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--why', action='store_true', help='explain each choice')
    ap.add_argument('--unused', action='store_true', help='what is still free')
    ap.add_argument('--sheet', nargs='?', const='KNEEBOARD.md', metavar='PATH',
                    help='write the cheat sheet and exit')
    ap.add_argument('--html', nargs='?', const='kneeboard.html', metavar='PATH',
                    help='write the same thing laid out in columns, for a'
                         ' second screen')
    args = ap.parse_args()

    if args.html:
        path, nb, na = html_sheet(args.html if os.path.isabs(args.html)
                                  else os.path.join(HERE, args.html))
        print(f'wrote {path}: {nb} bindings, {na} axes')
        return

    if args.sheet:
        path, nb, na = sheet(os.path.join(HERE, args.sheet)
                             if not os.path.isabs(args.sheet) else args.sheet)
        print(f'wrote {path}: {nb} bindings, {na} axes')
        return

    axes, buttons, placed, unmet, free = build()

    print(f'{len(placed)} needs matched, {len(buttons)} bindings, '
          f'{len(axes)} axes\n')
    for need, role, c, used in placed:
        where = c.direction(used[0]) if len(used) == 1 else ''
        print(f'  {need.what:24s} {role:8s} {c.kind:9s} {str(used):18s} '
              f'{c.label}' + (f' — {where}' if where else ''))
        if args.why:
            bits = [f'wants {"/".join(need.shape)}']
            if need.suits:
                bits.append(f'suits {need.suits}'
                            + (' ✓' if need.suits in c.suits else ' ✗'))
            if need.reflex:
                bits.append(f'reach: {c.reach}')
            print(f'      {", ".join(bits)}')
            if need.note:
                print(f'      {need.note}')
            f = max((FACTORY.get(a, 0) for a in need.air), default=0)
            if f:
                print(f'      factory HOTAS profiles binding this: {f}/29')
            print()

    if unmet:
        print(f'\n{len(unmet)} needs found no control:')
        for n in unmet:
            print(f'  {n.what:24s} wanted {"/".join(n.shape)}'
                  + (f', {n.suits}' if n.suits else '')
                  + (', reachable without regripping' if n.reflex else ''))

    if args.unused or free:
        print(f'\n{len(free)} controls left free:')
        for role, c in free:
            print(f'  {role:8s} {c.kind:9s} {str(c.buttons):18s} {c.label}'
                  f'   [{c.reach}]')


if __name__ == '__main__':
    main()
