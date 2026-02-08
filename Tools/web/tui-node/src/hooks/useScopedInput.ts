import { type Key, useFocus, useInput } from "ink";
import { useEffect } from "react";
import useDebugStore from "../store/useDebbugStore.js";
import { type EFocusAreal, useFocusStore } from "../store/useFocusStore.js";
import { ELogTypes } from "../types/global.enums.js";
import quitApplication from "../utils/helpers/quitApplication.js";

type InputCallback = (input: string, key: Key) => void;

interface UseScopedInputOptions {
    id: string;
    areal: EFocusAreal;
    keyMap?: InputCallback;
    autoFocus?: boolean;
}

/**
 * Enterprise Hook: Scoped Focus + Direct Input Callback.
 *
 * This hook manages Ink's focus and ensures that the provided input callback (keyMap)
 * only executes when the component is both focused and part of the active Areal.
 */
export const useScopedInput = ({ id, areal, keyMap, autoFocus = false }: UseScopedInputOptions) => {
    const { activeAreal, setActiveAreal } = useFocusStore();
    const { addLog } = useDebugStore();

    // 1. Manage Ink Focus
    const { isFocused } = useFocus({
        id,
        autoFocus,
    });

    // 2. Sync Global Areal State when focus changes
    useEffect(() => {
        if (isFocused && activeAreal !== areal) {
            addLog({
                type: ELogTypes.DEBUG,
                message: `Focus Area changed: ${activeAreal} -> ${areal} (via ${id})`,
                process: "useScopedInput",
            });
            setActiveAreal(areal);
        }
    }, [isFocused, activeAreal, areal, setActiveAreal, id, addLog]);

    // 3. Handle Keyboard Input with Scoped Activation
    useInput(
        (input, key) => {
            if (input === "q") {
                addLog({
                    type: ELogTypes.INFO,
                    message: "Quit requested via 'q' key",
                    process: "useScopedInput",
                });
                quitApplication();
            }
            if (keyMap) {
                keyMap(input, key as Key);
            }
        },
        { isActive: isFocused && activeAreal === areal },
    );

    return {
        isFocused,
        isArealActive: activeAreal === areal,
    };
};
