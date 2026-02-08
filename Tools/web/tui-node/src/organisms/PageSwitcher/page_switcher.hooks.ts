import { useStore } from "../../store/useStore.js";

export const usePageSwitcher = () => {
    const { currentPage } = useStore();
    return { currentPage };
};
