#pragma once
#include "tau.h"

enum class Faction{
Tau
};
const uint8_t* getFactionBitmap(Faction);
const char* getFactionName(Faction);