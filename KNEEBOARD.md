# Kneeboard — War Thunder

What sits under which finger, for air Simulator Battles and
helicopters. Action names are as they appear in the game menu.

**Generated** by `./plan.py --sheet` from `../sim-device-map` and the
game's own action list. Do not edit by hand -- recapture the hardware
or change `NEEDS` in `plan.py` and run it again.

War Thunder numbers buttons globally across devices, so the **WT**
column is what the menu shows: device offset plus the local number.

## R-VPC Stick WarBRD-D

Buttons 79–110, axes 16–21

| Control | WT | Air | Helicopter |
|---|---|---|---|
| Main trigger — first | `81` | Small-calibre guns | Small-caliber guns |
| Main trigger — second | `82` | Large-calibre guns | Large-caliber guns |
| Main trigger — third | `83` | Additional guns | Additional guns |
| Thumb top button | `85` | Fire air-to-air missile | Fire air-to-ground missile |
| Top thumb hat — push | `86` | Mouse look activation | Mouse look activation |
| Top thumb hat — up | `87` | Default view | Default view |
| Top thumb hat — left | `88` | Look back | Look back |
| Top thumb hat — down | `89` | Look down | Look down |
| Top thumb hat — right | `90` | — | Gunner View |
| Thumb bottom button | `91` | Fire rocket | Fire rockets |
| Bottom thumb hat — push | `92` | Lock Radar/IRST on target | Lock radar target on |
| Bottom thumb hat — up | `93` | Switch Radar/IRST search on/off | Switch radar search on/off |
| Bottom thumb hat — left | `94` | Select Radar/IRST target to lock | Select radar target to lock on |
| Bottom thumb hat — down | `95` | Change Radar/IRST mode | Change radar mode |
| Bottom thumb hat — right | `96` | Change Radar/IRST scope scale | Change radar scope scale |
| Grip thumb hat — push | `101` | Trim aircraft | Trim aircraft · Trim helicopter |
| Grip thumb hat — up | `102` | Elevator Trim Positive | Elevator Trim Positive |
| Grip thumb hat — left | `103` | Aileron Trim Left | Aileron Trim Left |
| Grip thumb hat — down | `104` | Elevator Trim Negative | Elevator Trim Negative |
| Grip thumb hat — right | `105` | Aileron Trim Right | Aileron Trim Right |
| Paddle button | `110` | Fire countermeasures | Fire countermeasures |

## L-VPC VMAX Prime Throttle

Buttons 28–78, axes 9–15

| Control | WT | Air | Helicopter |
|---|---|---|---|
| Pinky button | `28` | Weapon lock (air-to-air) | Weapon lock (air-to-air) |
| Middle finger button | `30` | Ignite boosters | Ignite boosters |
| Middle finger hat — push | `31` | Weapon lock (air-to-ground) | Weapon lock (air-to-ground) |
| Thumb two-way hat — push | `37` | Toggle Airbrake | — |
| Thumb two-way hat — forward | `38` | Toggle Gear | Toggle Gear |
| Thumb two-way hat — back | `40` | Toggle Gear | Toggle Gear |
| Thumb mini-stick — push | `42` | Drop bomb | Drop bomb |
| Thumb button | `43` | Radar/IRST beyond/within visual range combat | — |
| Bottom thumb button | `44` | — | Sight stabilization |
| Keyboard B1 button | `50` | — | Hover mode |
| Keyboard B2 button | `51` | — | Toggle SAS mode |
| Keyboard B3 button | `52` | Switch between Radar and IRST | — |
| Keyboard B4 button | `53` | Toggle Engine | Toggle Engine |
| Keyboard B5 button | `54` | Tactical Map | Tactical Map |
| Keyboard B6 button | `55` | Open bomb bay door | Open bomb bay door |
| Big red button | `56` | Drag chute | Drag chute |
| T1 rocker — up | `57` | Flaps Up | — |
| T1 rocker — down | `58` | Flaps Down | — |
| T2 rocker — up | `59` | Cockpit view | Cockpit view |
| T2 rocker — down | `60` | External View | External View |
| T3 rocker — up | `61` | — | Switch primary weapons |
| T3 rocker — down | `62` | — | Switch secondary weapons |
| APU button | `67` | — | Toggle Laser Designator |

## Axes

| Control | WT | Air | Helicopter |
|---|---|---|---|
| Main stick, left/right | `16` | ailerons | helicopter_cyclic_roll |
| Main stick, fore/aft | `17` | elevator | helicopter_cyclic_pitch | *(inverted)*
| Stick twist | `18` | rudder | helicopter_pedals |
| Mini-stick | `19` | sensor_cue_x | helicopter_atgm_aim_x |
| Mini-stick | `20` | sensor_cue_y | helicopter_atgm_aim_y |
| Analogue lever on the grip | `21` | brake_left · brake_right | — |
| Thumb mini-stick | `9` | camx | helicopter_camx |
| Thumb mini-stick | `10` | camy | helicopter_camy |
| Left throttle lever | `11` | throttle | helicopter_collective |
| Right side dial | `15` | zoom | — |

## Left free

Nothing here is wasted by accident -- these had no need that
wanted their shape.

| Control | Buttons | Reach |
|---|---|---|
| Left side dial (dial) | 29 | needs letting go |
| Thumb hat (hat4) | 46, 47, 48, 49, 45 | thumb, without releasing grip |
| T4 rocker (hat2) | 63, 64 | needs letting go |
| T5 rocker (hat2) | 65, 66 | needs letting go |
| E1 encoder (encoder) | 69, 70, 68 | needs letting go |
| E2 encoder (encoder) | 73, 72, 71 | needs letting go |
| Mode selector (selector) | 78, 77, 76, 75, 74 | needs letting go |
| Trigger initial lever (latch) | 80, 79 | index finger, on the grip |
| Stick encoder and click (encoder) | 100, 99, 97 | thumb, without releasing grip |
| Grip pinky button (button) | 109 | needs letting go |

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
