#!/usr/bin/env python3
"""Apply the source-only v0.200 integration after the existing iOS stack.

No private archive is read, downloaded, generated or bundled by this script.
The owned matching support package is selected from the device's Files container.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import shutil

PIN = "95130c3a8f8f746ea6412644571af4ee5de32366"
PATCH_SHA256 = "dc782b3611945be99c5f6576e5aa1b0524e956b7243f6b4cfecae1fb32874f90"
repo = Path(__file__).resolve().parents[1]
root = Path(sys.argv[1]).resolve()
patch = repo / "overlays/v0200/engine-integration-stage12.patch"

def git(*args, allow_conflicts=False):
    result = subprocess.run(["git", "-c", "core.safecrlf=false", "-c", "core.autocrlf=false", "-C", str(root), *args], capture_output=True, text=True)
    if result.returncode and not allow_conflicts:
        raise RuntimeError(result.stderr or result.stdout)
    return result

def edit(path, old, new):
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1, (str(path), old[:100])
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

assert git("rev-parse", "HEAD").stdout.strip() == PIN
assert hashlib.sha256(patch.read_bytes()).hexdigest() == PATCH_SHA256
assert not (root / ".selaco-v0200-integration.json").exists(), "Integration already attempted; inspect its result before retrying"
# Only the fetched public source tree is staged. Runtime private inputs live on
# the device and are never copied into this checkout or into Actions.
git("add", "--all")
result = git("apply", "--3way", "--index", str(patch), allow_conflicts=True)
conflicts = git("diff", "--name-only", "--diff-filter=U").stdout.splitlines()
assert not result.returncode or conflicts, result.stderr
assert set(conflicts) <= {"src/CMakeLists.txt", "src/d_main.cpp"}, conflicts
resolved = []
pattern = re.compile(r"^<<<<<<<[^\n]*\n(.*?)^=======\n(.*?)^>>>>>>>[^\n]*\n", re.M | re.S)
for relative in conflicts:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    blocks = list(pattern.finditer(text))
    assert blocks, relative
    if relative == "src/CMakeLists.txt":
        assert len(blocks) == 1 and "SELACO_PRIVATE_COMPILE_HARNESS" in blocks[0].group(2)
        # Independent iOS source properties and opt-in private compiler sources.
        text = pattern.sub(lambda m: m.group(1) + "\n" + m.group(2), text)
    else:
        # The reviewed conflicts are iOS startup instrumentation versus desktop
        # compiler-only startup/teardown guards. Retain the real iOS lifecycle.
        assert len(blocks) == 4, len(blocks)
        assert all("SELACO_IOS_" in m.group(1) for m in blocks)
        assert all("SELACO_PRIVATE_COMPILE_HARNESS" in m.group(2) or not m.group(2).strip() for m in blocks)
        text = pattern.sub(lambda m: m.group(1), text)
    assert not re.search(r"^(<<<<<<<|=======|>>>>>>>)", text, re.M)
    path.write_text(text, encoding="utf-8")
    git("add", "--", relative)
    resolved.append(relative)


# The iOS temporal overlay is applied before this 4.15.1 API migration.
# SetupFrame no longer receives CPU bones; do not retain its legacy capture.
models = root / "src/rendering/hwrenderer/hw_models.cpp"
assert "unsigned int size, int boneStartIndex)" in models.read_text(encoding="utf-8")
edit(models, "motionFrame2=frame2;motionBones=bones;",
     "motionFrame2=frame2;motionBones.Clear();boneIndexBase=boneStartIndex;")
assert "if(boneIndexBase>=0 && now.bones.empty())valid=false;" in models.read_text(encoding="utf-8")

reset_patch = repo / "overlays/v0200/recycled-map-reset.patch"
assert hashlib.sha256(reset_patch.read_bytes()).hexdigest() == "96b8cd9cc707f433aa0c410232d35b6c6d9939a322a2248ac26a81a777cb5101"
git("apply", str(reset_patch))

runtime = root / "src/common/platform/ios/i_platform_runtime.mm"
edit(runtime, "extern int GameMain();\n", "extern int GameMain();\nvoid I_ShowFatalError(const char *message);\n")
old = '''        NSString *baseArchive = [bundlePath stringByAppendingPathComponent:@"gzdoom.pk3"];
        if (![[NSFileManager defaultManager] isReadableFileAtPath:baseArchive]) {
            SelacoIOSReportLicensedAssetProbe(
                "public_support_missing",
                "The IPA lacks its generated public gzdoom.pk3 support archive");
            return;
        }
'''
new = '''        // The v0.200 engine requires the owner's matching support scripts and
        // shaders. The archive stays private in Files, outside the IPA and CI.
        NSString *baseArchive = [DiagnosticDirectory()
            stringByAppendingPathComponent:@"Engine/gzdoom.pk3"];
        NSDictionary *coreAttributes = [[NSFileManager defaultManager]
            attributesOfItemAtPath:baseArchive error:nil];
        NSString *coreDigest = SHA256ForFile(baseArchive);
        if ([coreAttributes fileSize] != 2670116 || !HasZipSignature(baseArchive) ||
            ![coreDigest isEqualToString:
                @"02416457ce5d563673d02f8e46cdf1a125334bad68bdd68219b62d3263061ddd"]) {
            I_ShowFatalError("Matching v0.200 support package missing or changed. "
                "Place your owned gzdoom.pk3 in Files > SelacoiOS Engine Init > "
                "Selaco > Engine. Existing saves, settings and Mods are preserved.");
            return;
        }
        SelacoIOSReportLicensedAssetProbe("owned_support_validated",
            "Matching owned v0.200 core SHA256 verified; archive remains private");
'''
edit(runtime, old, new)
edit(runtime, "        // Optional, exact allowlisted private mod only. Never enumerate Mods.\n",
     '''        arguments.emplace_back("-selaco-owned-core");
        arguments.emplace_back(baseArchive.fileSystemRepresentation);
        // Optional, exact allowlisted private mod only. Never enumerate Mods.
''')
text = runtime.read_text(encoding="utf-8")
assert text.count('"Savegames-candidate"') == 2, "Expected both platform and explicit save roots"
runtime.write_text(text.replace('"Savegames-candidate"', '"Savegames-v0200"'), encoding="utf-8")
dmain = root / "src/d_main.cpp"
edit(dmain, "\twad = BaseFileSearch(BASEWAD, NULL, true, GameConfig);\n",
     '''\twad = Args->CheckValue("-selaco-owned-core");
\tif (wad == nullptr) wad = BaseFileSearch(BASEWAD, NULL, true, GameConfig);
''')
edit(dmain, '\tSelacoIOSReportLicensedAssetProbe("public_support_loaded", wad);\n',
     '''\tSelacoIOSReportLicensedAssetProbe(Args->CheckValue("-selaco-owned-core") ?
\t\t"owned_support_loaded" : "public_support_loaded", wad);
''')
motion_header = root / "src/common/rendering/hwrenderer/data/hw_motion_diagnostic.h"
shutil.copyfile(repo / "overlays/gzselaco-ios/i_core_shader_contract.h", motion_header.with_name("i_core_shader_contract.h"))
edit(motion_header, "#include <cstdlib>\n", '#include <cstdlib>\n#include "i_core_shader_contract.h"\n')
edit(motion_header, "    return enabled;\n", "    return enabled && SelacoCoreHasMotionShaders();\n")
assert 'option(SELACO_PRIVATE_COMPILE_HARNESS "Build the isolated private semantic compiler" OFF)' in (root / "src/CMakeLists.txt").read_text()
assert 'gEngineProbeStatus.Record(phase, detail)' in runtime.read_text(), "Persistent fatal diagnostics required"
receipt = {"source_pin": PIN, "integration_patch_sha256": PATCH_SHA256,
    "recycled_map_reset_patch_sha256": "96b8cd9cc707f433aa0c410232d35b6c6d9939a322a2248ac26a81a777cb5101",
    "reviewed_merge_conflicts": resolved, "owned_core_device_path": "Documents/Selaco/Engine/gzdoom.pk3",
    "new_save_directory": "Documents/Selaco/Savegames-v0200", "old_saves_preserved": True,
    "experimental_temporal_requires_loaded_core_MRT_outputs": True,
    "private_assets_copied_or_bundled": False, "normal_version_check_bypassed": False,
    "private_compile_harness_enabled": False, "apple_build_started": False}
(root / ".selaco-v0200-integration.json").write_text(json.dumps(receipt, indent=2) + "\n")
print("Applied genuine v4.15.1/v0.200 source integration; matching owned support stays in device Files")
