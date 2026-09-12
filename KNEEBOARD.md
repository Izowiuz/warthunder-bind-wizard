# Kneeboard — War Thunder

What sits under which finger, for air Simulator Battles and
helicopters. Action names are as they appear in the game menu.

**Generated** by `./plan.py --sheet` from `../sim-device-map` and the
game's own action list. Do not edit by hand -- recapture the hardware
or change `NEEDS` in `plan.py` and run it again.

War Thunder numbers buttons globally across devices, so the **WT**
column is what the menu shows: device offset plus the local number.

## R-VPC Stick WarBRD-D

Buttons 51–82, axes 7–12

| Control | WT | Air | Helicopter |
|---|---|---|---|
| Main trigger — first | `53` | Small-calibre guns | Small-caliber guns |
| Main trigger — second | `54` | Large-calibre guns | Large-caliber guns |
| Main trigger — third | `55` | Additional guns | Additional guns |
| Thumb top button | `57` | Fire air-to-air missile | Fire air-to-ground missile |
| Top thumb hat — push | `58` | Mouse look activation | Mouse look activation |
| Top thumb hat — up | `59` | Default view | Default view |
| Top thumb hat — left | `60` | Look back | Look back |
| Top thumb hat — down | `61` | Look down | Look down |
| Top thumb hat — right | `62` | Bomber View | Bomber View · Gunner View |
| Thumb bottom button | `63` | Fire rocket | Fire rockets |
| Bottom thumb hat — push | `64` | Lock Radar/IRST on target | Lock radar target on |
| Bottom thumb hat — up | `65` | Switch Radar/IRST search on/off | Switch radar search on/off |
| Bottom thumb hat — left | `66` | Select Radar/IRST target to lock | Select radar target to lock on |
| Bottom thumb hat — down | `67` | Change Radar/IRST mode | Change radar mode |
| Bottom thumb hat — right | `68` | Change Radar/IRST scope scale | Change radar scope scale |
| Grip thumb hat — push | `73` | Trim aircraft | Trim aircraft · Trim helicopter |
| Grip thumb hat — up | `74` | Elevator Trim Positive | Elevator Trim Positive |
| Grip thumb hat — left | `75` | Aileron Trim Left | Aileron Trim Left |
| Grip thumb hat — down | `76` | Elevator Trim Negative | Elevator Trim Negative · Reset trimming |
| Grip thumb hat — right | `77` | Aileron Trim Right | Aileron Trim Right |
| Paddle button | `82` | Fire countermeasures | Fire countermeasures |

## L-VPC VMAX Prime Throttle

Buttons 0–50, axes 0–6

| Control | WT | Air | Helicopter |
|---|---|---|---|
| Pinky button | `0` | Weapon lock (air-to-air) | Weapon lock (air-to-air) |
| Middle finger button | `2` | Ignite boosters | Ignite boosters |
| Middle finger hat — push | `3` | Weapon lock (air-to-ground) | Weapon lock (air-to-ground) |
| Thumb two-way hat — push | `9` | Toggle Airbrake | — |
| Thumb two-way hat — forward | `10` | Toggle Gear | Toggle Gear |
| Thumb two-way hat — back | `12` | Toggle Gear | Toggle Gear |
| Thumb mini-stick — push | `14` | Drop bomb | Drop bomb |
| Thumb button | `15` | Radar/IRST beyond/within visual range combat | — |
| Bottom thumb button | `16` | — | Sight stabilization |
| Keyboard B1 button | `22` | — | Hover mode |
| Keyboard B2 button | `23` | — | Toggle SAS mode |
| Keyboard B3 button | `24` | Switch between Radar and IRST | — |
| Keyboard B4 button | `25` | Toggle Engine | Toggle Engine |
| Keyboard B5 button | `26` | Tactical Map | Tactical Map |
| Keyboard B6 button | `27` | Open bomb bay door | Open bomb bay door |
| Big red button | `28` | Drag chute | Drag chute |
| T1 rocker — up | `29` | Flaps Up | — |
| T1 rocker — down | `30` | Flaps Down | — |
| T2 rocker — up | `31` | Cockpit view | Cockpit view |
| T2 rocker — down | `32` | External View | External View |
| T3 rocker — up | `33` | — | Switch primary weapons |
| T3 rocker — down | `34` | — | Switch secondary weapons |
| APU button | `39` | — | Toggle Laser Designator |

## Axes

| Control | WT | Air | Helicopter |
|---|---|---|---|
| Main stick, left/right | `7` | ailerons | helicopter_cyclic_roll |
| Main stick, fore/aft | `8` | elevator | helicopter_cyclic_pitch | *(inverted)*
| Stick twist | `9` | rudder | helicopter_pedals |
| Mini-stick | `10` | sensor_cue_x | helicopter_atgm_aim_x |
| Mini-stick | `11` | sensor_cue_y | helicopter_atgm_aim_y |
| Analogue lever on the grip | `12` | brake_left · brake_right | — |
| Thumb mini-stick | `0` | camx | helicopter_camx |
| Thumb mini-stick | `1` | camy | helicopter_camy |
| Left throttle lever | `2` | throttle | helicopter_collective |
| Right side dial | `6` | zoom | — |

## Left free

Nothing here is wasted by accident -- these had no need that
wanted their shape.

| Control | Buttons | Reach |
|---|---|---|
| Left side dial (dial) | 1 | needs letting go |
| Thumb hat (hat4) | 18, 19, 20, 21, 17 | thumb, without releasing grip |
| T4 rocker (hat2) | 35, 36 | needs letting go |
| T5 rocker (hat2) | 37, 38 | needs letting go |
| E1 encoder (encoder) | 41, 42, 40 | needs letting go |
| E2 encoder (encoder) | 45, 44, 43 | needs letting go |
| Mode selector (selector) | 50, 49, 48, 47, 46 | needs letting go |
| Trigger initial lever (latch) | 52, 51 | index finger, on the grip |
| Stick encoder and click (encoder) | 72, 71, 69 | thumb, without releasing grip |
| Grip pinky button (button) | 81 | needs letting go |

## Check in flight

- **Elevator trim direction** — hat up should raise the nose.
- **Zoom axis** — it rests at minimum, so the view should start
  unzoomed. If not, invert it.
- **View mini-stick** — your head should go where your thumb goes.

## Undo

```
./wt-bind-preset.py --restore
```

The game must be closed: it rewrites `machine.blk` on exit.
