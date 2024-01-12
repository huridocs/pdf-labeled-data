import { createContext } from 'react';

export const SHOW_TOKENS = 'hideTokens';
export const HIDE_LABELS_NAMES = 'showLabelNames';

interface _OptionsStore {
    options: { [key: string]: boolean };
    setOptions: (option: { [key: string]: boolean }) => void;
}

export const OptionsStore = createContext<_OptionsStore>({
    options: {
        [SHOW_TOKENS]: false,
        [HIDE_LABELS_NAMES]: false,
    },
    setOptions: (_: { [key: string]: boolean }) => {},
});
