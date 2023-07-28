import { createContext } from 'react';

export const SHOW_TOKENS = 'hideTokens';
export const READING_ORDER = 'readingOrder';

interface _OptionsStore {
    options: { [key: string]: boolean };
    setOptions: (option: { [key: string]: boolean }) => void;
}

export const OptionsStore = createContext<_OptionsStore>({
    options: {
        [READING_ORDER]: false,
        [SHOW_TOKENS]: false,
    },
    setOptions: (_: { [key: string]: boolean }) => {},
});
