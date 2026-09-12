# warthunder-bind-wizard

Full HOTAS control preset for **War Thunder on Linux** (native Steam client),
aimed at air Simulator Battles + helicopters on a VIRPIL VMAX Prime throttle
and a VPC Stick WarBRD-D. Sibling of [dcs-bind-wizard](../dcs-bind-wizard) and
[elite-dangerous-bind-wizard](../elite-dangerous-bind-wizard).

## Why a script instead of clicking in the menu

War Thunder keeps its bindings in
`~/.config/WarThunder/Saves/<uid>/production/machine.blk`, in plain text, so a
preset can be written offline — no 300 rows of menu clicking, and the result is
reviewable as a diff. The script rewrites only that file's `controls{}` block
and leaves every other byte (graphics, audio, the lot) alone, CRLF line endings
included.

## How War Thunder numbers a HOTAS

Axes and buttons are numbered **globally across devices**, in the order the
devices appear in `deviceMapping`:

| device                     | axes  | buttons |
|----------------------------|-------|---------|
| L-VPC VMAX Prime Throttle  | 0–6   | 0–50    |
| R-VPC Stick WarBRD-D       | 7–12  | 51–82   |

so `WT axisId = axesOffset + local axis` and `WT joyButton = buttonsOffset +
local button`. The plan in `wt-bind-preset.py` is written in local
`(device, index)` terms and resolved against the `deviceMapping` the game
itself recorded, so it survives a change of offsets — replug the sticks in a
different order, start the game once, re-run.

Air and helicopter actions are separate control contexts (`ID_FLAPS_UP` vs
`ID_FLAPS_UP_HELICOPTER`), so one physical button carries one of each without
conflicting. The script's conflict check knows the difference: an action is
air-only when the game ships a `_HELICOPTER` twin for it, and shared when it
does not.

## Where the action names come from

`wt-actions.json` is harvested from the game's own archives, not hardcoded:

- `aces.vromfs.bin` and `lang.vromfs.bin` are `VRFx` containers — zstd, with
  the first and last 16 bytes of the compressed body obfuscated by a fixed XOR
  key. Deobfuscate, decompress, and you get a flat filesystem: a table of
  `u64` name pointers and a table of `(offset, size)` pairs.
- `lang/controls.csv` inside `lang.vromfs.bin` holds every bindable action
  (651 of them) and axis name (680) with translations, which is what the
  script validates the plan against — an invented `ID_` is silently dropped by
  the game, so the script refuses to write if one does not exist.
- the shared nametable (`\xff?nm`) lists the names actually used as keys in
  the shipped `.blk` presets, which is a decent proxy for "Gaijin binds this
  by default".

## Where the plan comes from

Not from a table in this repo. [`../sim-device-map`](../sim-device-map) knows
the **shape** of every control on the hardware -- which buttons form one hat,
which trigger stages are cumulative, what you can reach without letting go of
the stick -- and `plan.py` states what a pilot needs as a shape rather than a
button number:

```python
Need('Countermeasures', ('paddle', 'button'), air=['ID_FLARES'],
     suits='reflex', reflex=True)
```

`reflex=True` disqualifies every control the map marks `needs letting go`, so
countermeasures land on the paddle because the paddle is what your little
finger reaches, not because anyone remembered where the paddle is. The first
version of this wizard did remember, and was wrong twice.

`./plan.py --why` prints the reasoning for each choice, including how many of
the game's 29 factory HOTAS profiles bind that action.

`./plan.py --sheet` regenerates [`KNEEBOARD.md`](KNEEBOARD.md) from the same
data, so the cheat sheet cannot drift from what is actually bound.

## First run

Two files are built from the installed game rather than kept here:
`wt-actions.json` is Gaijin's own localisation, and the factory ranking is
derived from the joystick profiles they ship.

```bash
./harvest.py                           # or --game-dir /path/to/War\ Thunder
```

It unpacks the `VRFx` archives (zstd, with the first and last 16 bytes of the
body XORed against a fixed key), reads `lang/controls.csv` for every bindable
action, and decodes the binary `.blk` presets -- zstd against a dictionary
shipped beside them, key names in a nametable shared across the archive -- to
count what a HOTAS is expected to carry. Re-run it after a game patch.

## Flow

```bash
./harvest.py                 # once, and after a game patch adds actions
./plan.py --why              # what goes where, and why
./wt-bind-preset.py          # write it into machine.blk (game closed)
./plan.py --sheet --html     # KNEEBOARD.md + the columns page
```

Change the hardware: capture it in [`sim-device-map`](../sim-device-map), then
re-run `plan.py`. Nothing here describes your devices.

`plan.py` needs that repo as a sibling directory, or `SIM_DEVICE_MAP` pointing
at it.

## Usage

```bash
./plan.py                              # what goes where
./plan.py --why                        # and why
./plan.py --sheet                      # regenerate KNEEBOARD.md
./wt-bind-preset.py --dry-run          # print the plan and the resolved ids
./wt-bind-preset.py --render /tmp/x    # render the result somewhere harmless
./wt-bind-preset.py                    # write machine.blk (timestamped backup)
./wt-bind-preset.py --restore          # roll back to the newest backup
```

The game must be closed: it rewrites `machine.blk` on exit and would throw the
changes away. The script checks and refuses.

## Afterwards

With the bindings in place, use the game's own **Controls → save preset** once.
That writes a preset in War Thunder's own format, which is the thing to reload
after a patch resets something.

## Known rough edges

- **Elevator trim direction.** `ID_TRIM_ELEVATOR_PLUS` is on hat A up. If it
  trims the wrong way, swap `_PLUS` and `_MINUS` in `BUTTONS`.
- **Zoom axis.** Throttle axis 5 rests at its minimum, which should read as
  "not zoomed". If the view starts zoomed in, add `inverse` to the `zoom` row
  in `AXES`.
- **Head tracking.** opentrack's evdev/uinput output would appear as a third
  joystick and could drive `camx`/`camy` directly — but it must be connected
  *before* the game starts, or it lands at a different `axesOffset` and every
  id above shifts. Until then the throttle's thumb stick does head look.
