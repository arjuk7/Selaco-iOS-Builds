#pragma once
#include "filesystem.h"
#include "zstring.h"
#include "printf.h"

// Selecting the matching owned core also selects its genuine shaders. Temporal
// rendering requires the experimental MRT outputs in the actual loaded files;
// the existence of extra render targets alone does not establish this contract.
inline bool SelacoCoreHasMotionShaders()
{
    static int available = -1;
    if (available >= 0) return available != 0;
    const int vertex = fileSystem.CheckNumForFullName("shaders/glsl/main.vp");
    const int fragment = fileSystem.CheckNumForFullName("shaders/glsl/main.fp");
    if (vertex < 0 || fragment < 0) return false;
    const auto vp = fileSystem.ReadFile(vertex), fp = fileSystem.ReadFile(fragment);
    const FString vertexText(vp.string(), vp.size()), fragmentText(fp.string(), fp.size());
    available = vertexText.IndexOf("vMotionCurrentClip") >= 0 &&
        vertexText.IndexOf("vMotionPreviousClip") >= 0 &&
        fragmentText.IndexOf("FragMotionDiagnostic") >= 0 &&
        fragmentText.IndexOf("FragReactiveCoverage") >= 0;
    if (!available)
        Printf("Selaco v0.200: loaded core lacks experimental motion/reactive shader outputs; temporal and frame generation unavailable, ordinary rendering selected.\n");
    return available != 0;
}
