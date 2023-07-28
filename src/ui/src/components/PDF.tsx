import React, { useContext } from 'react';

import { PDFStore } from '../context';
import { Page } from './Page';

export const PDF = () => {
    const pdfStore = useContext(PDFStore);

    // TODO (@codeviking): Use error boundaries to capture these.
    if (!pdfStore.doc) {
        throw new Error('No Document');
    }
    if (!pdfStore.pages) {
        throw new Error('Document without Pages');
    }

    return (
        <>
            {pdfStore.pages.map((p) => {
                return <Page key={p.page.pageNumber} pageInfo={p} onError={pdfStore.onError} />;
            })}
        </>
    );
};
