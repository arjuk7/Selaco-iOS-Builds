# Startup fatal persistence

An engine startup exception reaches `GameMain`'s `std::exception` handler,
which calls `I_ShowFatalError` and returns `-1` after cleanup. The iOS callback
previously replaced the reported reason with each cleanup event and finally
`engine_probe_returned`. The runtime breadcrumb retained the error, while the
status files and UIKit label lost it. A graphics-failure hypothesis is
contradicted by the captured first-frame marker and explicit compiler error.

The diagnostic sink now keeps the first `engine_fatal_error` for the current
asset/engine attempt. It serializes selection, status writes, and notification
enqueueing with one mutex. `engine-init-status.txt`,
`licensed-asset-status.txt`, and the UIKit notification retain that error through
cleanup and return. Raw events still append to `runtime-bootstrap.txt`, and
renderer status still follows renderer events. The full fatal is also appended
to `zscript-compile.log`. Beginning a new attempt clears the retained failure.

The distinguishing device evidence is a raw `engine_fatal_error`, subsequent
cleanup and `engine_probe_returned` breadcrumbs, and a final status file/UI
that still contains the original fatal detail. The competing stale-attempt
hypothesis is covered by explicitly resetting at the next probe entry.

Validation on Windows used MSVC C++17 with warnings as errors. The native test
covers the captured fatal/cleanup/return sequence, secondary failures, late
frame events, long and UTF-8 reasons, null inputs, normal results, and a new
attempt. It also replays the complete captured device breadcrumb log. A
separate contract check verifies the real materialized iOS source routes the
retained reason to both status files, the console log, and UIKit while retaining
the raw breadcrumb and renderer paths.

The complete build36 patch stack materializes successfully with this change.
This is a diagnostics repair only. No version constants, script acceptance,
native game fields, saves, input layouts, or asset selection change. Apple SDK
compilation and physical-device verification remain outstanding. No workflow
run or phone launch was performed for this change.
