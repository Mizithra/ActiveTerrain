#include "icons.h"
const uint8_t* getFactionBitmap(Faction f){switch(f){case Faction::Tau:return tauIcon;default:return nullptr;}}
const char* getFactionName(Faction f){switch(f){case Faction::Tau:return "Tau Empire";default:return "";}}