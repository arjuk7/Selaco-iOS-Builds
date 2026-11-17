#include "i_engine_probe_status.h"
#include <cassert>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

int main(int argc, char **argv)
{
    SelacoEngineProbeStatus status;
    status.BeginAttempt();
    assert(status.Record("engine_probe_starting", "starting") ==
        "phase=m4_engine_probe_starting starting");
    const std::string detail =
        "Script error, \"Selaco.ipk3:zscript\" line 1:\n"
        "ZScript version 4.15.1 is required; engine supports 4.13.0.\n";
    const auto fatal = status.Record("engine_fatal_error", detail.c_str());
    assert(fatal == "phase=m4_engine_fatal_error " + detail);
    // Replay the captured GameMain error -> graphics teardown -> -1 sequence.
    for (const auto *phase : {"engine_graphics_shutdown_entered",
        "engine_graphics_shutdown_passed", "ini_write_failed",
        "engine_probe_returned", "engine_first_frame_presented"}) {
        assert(status.Record(phase, "later event") == fatal);
    }
    assert(status.Record("engine_fatal_error", "secondary failure") == fatal);

    // A new attempt gets its own result, without reading a stale disk log.
    status.BeginAttempt();
    assert(status.Record("asset_missing", "copy data") ==
        "phase=m4_asset_missing copy data");
    assert(status.Record("engine_probe_returned", "73") ==
        "phase=m4_engine_probe_returned 73");
    assert(status.Record(nullptr, nullptr) == "phase=m4_unknown ");
    assert(status.Record("engine_fatal_error", "") == "phase=m4_engine_fatal_error ");
    assert(status.Record("engine_probe_returned", "-1") == "phase=m4_engine_fatal_error ");

    status.BeginAttempt();
    const std::string longReason = "Compilation failed: \xc3\xa9\n" + std::string(16384, 'x');
    const auto longFatal = status.Record("engine_fatal_error", longReason.c_str());
    assert(longFatal == "phase=m4_engine_fatal_error " + longReason);
    assert(status.Record("engine_probe_returned", "-1") == longFatal);

    if (argc == 2) {
        std::ifstream log(argv[1]);
        assert(log.is_open());
        std::vector<std::pair<std::string, std::string>> events;
        std::string line;
        while (std::getline(log, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            if (line.rfind("phase=m4_", 0) == 0) {
                const auto space = line.find(' ');
                events.emplace_back(line.substr(9, space == std::string::npos ? space : space - 9),
                    space == std::string::npos ? "" : line.substr(space + 1));
            } else if (!events.empty()) {
                events.back().second += "\n" + line;
            }
        }
        status.BeginAttempt();
        std::string finalStatus;
        for (const auto &event : events) {
            if (event.first == "engine_probe_starting") status.BeginAttempt();
            finalStatus = status.Record(event.first.c_str(), event.second.c_str());
        }
        assert(finalStatus.rfind("phase=m4_engine_fatal_error ", 0) == 0);
        assert(finalStatus.find("4.15.1") != std::string::npos);
        assert(finalStatus.find("4.13.0") != std::string::npos);
        assert(finalStatus.find("bounded probe code -1") == std::string::npos);
        std::cout << "PASS: captured device event replay preserves the version fatal through cleanup and return\n";
    }
}
