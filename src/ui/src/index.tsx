/**
 * This is the main entry point for the UI. You should not need to make any
 * changes here unless you want to update the theme.
 *
 * @see https://github.com/allenai/varnish
 */

import React from 'react';
import ReactDOM from 'react-dom';
import { ThemeProvider } from '@allenai/varnish';
import '@allenai/varnish/dist/varnish.css';

import App from './App';

ReactDOM.render(
    <ThemeProvider>
        <App />
    </ThemeProvider>,
    document.getElementById('root')
);
