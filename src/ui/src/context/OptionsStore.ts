import { createContext } from 'react';

export const SHOW_TOKENS = 'hideTokens';

interface _OptionsStore {
    options: { [key: string]: boolean };
    setOptions: (option: { [key: string]: boolean }) => void;
}

export const OptionsStore = createContext<_OptionsStore>({
    options: {
        [SHOW_TOKENS]: false,
    },
    setOptions: (_: { [key: string]: boolean }) => {},
});
