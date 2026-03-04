import { configureStore } from "@reduxjs/toolkit";
import { type TypedUseSelectorHook, useDispatch, useSelector } from "react-redux";
import rootMiddleware from "./rootMiddleware";
import rootReducers from "./rootReducers";

const store = configureStore({
    reducer: rootReducers,
    devTools: true,
    middleware: (gDM) => gDM().concat(rootMiddleware),
});

export default store;

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export type AppStore = typeof store;
export type AppThunk<ReturnType = void> = () => ReturnType;

export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
export const useAppDispatch: () => AppDispatch = useDispatch;
