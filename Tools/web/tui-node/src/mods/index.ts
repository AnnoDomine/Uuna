import { UtilsMod } from "./available/utilsMod.js";
import { modRegistry } from "./modRegistry.js";

// Register all mods here
export const initMods = () => {
    modRegistry.register(UtilsMod);
    // modRegistry.register(YourNextMod);
};
