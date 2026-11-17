#pragma once

#include <cstring>
#include <string>

// Caller serializes BeginAttempt and Record with the diagnostic sink writes.
// A fatal's original detail survives cleanup and GameMain's generic return.
class SelacoEngineProbeStatus
{
public:
    void BeginAttempt() { fatalLine.clear(); }

    std::string Record(const char *phase, const char *detail)
    {
        const char *name = phase == nullptr ? "unknown" : phase;
        std::string line = std::string("phase=m4_") + name + " " +
            (detail == nullptr ? "" : detail);
        if (fatalLine.empty() && std::strcmp(name, "engine_fatal_error") == 0) {
            fatalLine = line;
        }
        return fatalLine.empty() ? line : fatalLine;
    }

private:
    std::string fatalLine;
};
