"""Check real materialized sink wiring; native behavior has a separate C++ test."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
repo = Path(__file__).resolve().parents[1]
ios = root / 'src/common/platform/ios'
source = (ios / 'i_platform_runtime.mm').read_text(encoding='utf-8')
callback = source.split('extern "C" void SelacoIOSReportLicensedAssetProbe(const char *phase, const char *detail)\n{', 1)[1].split('\nvoid CalculateCPUSpeed()', 1)[0]
assert callback.index('std::lock_guard<std::mutex>') < callback.index('WriteBreadcrumb(line)')
assert 'gEngineProbeStatus.Record(phase, detail)' in callback
for target in ('licensedPath', 'enginePath'):
    assert f'[visibleLine writeToFile:{target} ' in callback
    assert f'[line writeToFile:{target} ' not in callback
assert 'userInfo:@{@"text": visibleLine}' in callback
assert 'AppendEngineConsoleLog(line.UTF8String)' in callback
assert '[line writeToFile:rendererPath ' in callback
assert source.count('gEngineProbeStatus.BeginAttempt();') == 1
attempt = source.split('void RunLicensedAssetProbe()\n{', 1)[1]
assert attempt.index('gEngineProbeStatus.BeginAttempt();') < attempt.index('FindLicensedAssetPath();')
assert '"engine_probe_returned"' in attempt
stub = (ios/'i_engine_startup_stubs.mm').read_text(encoding='utf-8')
assert '"engine_fatal_error"' in stub
assert (ios/'i_engine_probe_status.h').read_bytes() == (repo/'overlays/gzselaco-ios/i_engine_probe_status.h').read_bytes()
print('PASS: raw breadcrumb and renderer sink retained; fatal reaches console, both terminal status files, and UIKit; new attempt resets')
