# Selaco v0.200 candidate

The updated game data requires ZScript 4.15.1. Build36 supported 4.13.0 and its
TopSprite fix did not address that independent startup failure.

This candidate retains GZSelaco source pin
`95130c3a8f8f746ea6412644571af4ee5de32366` and integrates the genuine compiler,
runtime and required game providers from GZDoom
`c26ce2e6ca2a0c770f140cb25dde0d30073ca8f7`. It preserves Selaco's native
contracts, with the additional owned-reference contracts reconstructed from
local evidence. The ordinary content-version check remains active at 4.15.1.

The source integration includes live LIGHTMAP/LIGHTGRP loading and checksum
policy, real source textures and layer targets, visibility queues and compositor
updates, ordinary and heavy probes, renderer uniform transport, actor probe
index spawn/save lifecycle, and the existing audio effects backend integration.
Saved LightGroup script state replays through the matching owned support
scripts and their normal Tick calls. No guessed native save keys were added.

The iOS driver applies the source-only integration after the existing controls,
renderer, audio and atomic-save patches. Its reviewed merge resolutions retain
the iOS startup lifecycle. The compiler-only target defaults to OFF and the iOS
configure command explicitly sets it OFF. The candidate's build number is 37.

## Private device input

The matching owned support archive must be copied privately to:

`Documents/Selaco/Engine/gzdoom.pk3`

Its size is **2,670,116 bytes** and SHA-256 is
`02416457ce5d563673d02f8e46cdf1a125334bad68bdd68219b62d3263061ddd`.
The app checks both before selecting it as the engine core. A missing or changed
archive produces a persistent fatal message identifying the required Files
location. The archive is not included in this repository, Actions or the IPA.

The already updated `Documents/Selaco/Selaco.ipk3` remains the game payload.
Saves for this version use **Documents/Selaco/Savegames-v0200**. Existing save
directories, settings, Mods and custom controls remain in place. The developer
states that pre-Chapter 2 saves are incompatible with Machines of War.

Brutal Selaco remains a separate optional input with its existing exact archive
identity check. The restored native `enablemods` setting controls whether it is
mounted. The archive is neither deleted nor altered.

## Essential evidence and limits

The private Windows engine linked successfully. The real complete base-script
initialization passed using the owned support archive and updated game data,
then exited cleanly with the intentional code 1337. The run loaded 371 support
lumps and 55,360 game lumps, indexed 30,094 game textures and initialized 1,144
sound-file entries. It loaded no mod and entered no game loop, renderer, input
device or phone session. Existing deprecation and missing-class warnings
were reported; no script errors remained.

The iOS source materialization and reviewed integration merge passed locally.
No Apple job has been dispatched. One coordinated Apple build is the next step;
menu/gameplay/save-load and GPU behavior remain for the user's runtime test.
Brutal has not been compiled separately because its exact archive is absent from
the authorized desktop input path.

The matching owned shaders do not contain the experimental motion/reactive MRT
outputs. A check of the actual loaded shader resources therefore keeps temporal
rendering and frame generation unavailable for this core and selects ordinary
rendering. No private shader is modified or replaced by an older public shader.

Source patch SHA-256:
`dc782b3611945be99c5f6576e5aa1b0524e956b7243f6b4cfecae1fb32874f90`.
The small recycled-map reset follow-up is
`96b8cd9cc707f433aa0c410232d35b6c6d9939a322a2248ac26a81a777cb5101`.
It clears prior lighting ownership even when rebuilt nodes prevent using the
new map's baked surface mapping.

Upstream license headers and third-party license files remain in the source
patch. The patch contains source and public support definitions; it contains no
owned archive, binary, retail script body, save or private shader body.
