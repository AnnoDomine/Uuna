export interface IMod {
    name: string;
    description: string;
    execute: (args: string[]) => string[]; // Returns lines for the Info-Box
    getSuggestions: (args: string[]) => string[];
}

class ModRegistry {
    private mods: Map<string, IMod> = new Map();

    register(mod: IMod) {
        this.mods.set(mod.name, mod);
    }

    getMod(name: string): IMod | undefined {
        return this.mods.get(name);
    }

    getAllModNames(): string[] {
        return Array.from(this.mods.keys());
    }
}

export const modRegistry = new ModRegistry();
