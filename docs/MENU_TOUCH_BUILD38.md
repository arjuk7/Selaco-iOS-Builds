# Build 38 menu tap repair

Observed: the v0.200 Mods Temporarily Disabled modal renders but cannot be dismissed with the touch overlay.
Model: UIKit owns all touches. Menu mode previously emitted only GUI keyboard navigation; taps outside overlay buttons were discarded. The original engine already supports absolute GUI mouse events.
Competing hypothesis: modal script state fails or ignores mouse input. The new SELACO_TOUCH_MENU_TAP log distinguishes delivery from a downstream menu issue. No retail scripts were inspected or changed.
Change: direct taps outside menu overlay controls queue a normalized point and emit move/down/up together on the engine thread. Existing arrows, confirm and back remain unchanged. Editor, cancelled touches, mode transitions, gameplay and drags do not emit menu taps. Saved layouts are unchanged.
Focused check: touch_input_test passes with C++17 MSVC, including event order, coordinates, invalid inputs, cancellation/reset and gameplay isolation. Objective-C++ Apple compilation and phone modal test remain pending.
