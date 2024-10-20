import React, { useContext, useCallback, useState, useEffect } from 'react';
import styled, { ThemeContext } from 'styled-components';
import { useParams } from 'react-router-dom';
import * as pdfjs from 'pdfjs-dist';
import { PDFDocumentProxy, PDFDocumentLoadingTask } from 'pdfjs-dist/types/display/api';
import { Result, Progress } from '@allenai/varnish';

import { QuestionCircleOutlined } from '@ant-design/icons';

import { PDF, CenterOnPage } from '../components';
import { SidebarContainer } from '../components/sidebar';
import {
    pdfURL,
    PagesTokens,
    Label,
    getAnnotations,
    getLabels,
    PdfStatus,
    getPdfsStatues,
    getTokens,
} from '../api';
import {
    PDFPageInfo,
    Annotation,
    AnnotationStore,
    PDFStore,
    PdfAnnotations,
    DatasetsStore,
    TASKS,
} from '../context';

import * as listeners from '../listeners';
import { Tasks } from '../components/sidebar/Tasks';
import { Options } from '../components/sidebar/Options';
import { Datasets } from '../components/sidebar/Datasets';
import { Labels } from '../components/sidebar/Labels';

import { Pdfs } from '../components/sidebar/Pdfs';
import { Annotations } from '../components/sidebar/Annotations';

// This tells PDF.js the URL the code to load for it's webworker, which handles heavy-handed
// tasks in a background thread. Ideally we'd load this from the application itself rather
// than from the CDN to keep things local.
// TODO (@codeviking): Figure out how to get webpack to package up the PDF.js webworker code.
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

enum ViewState {
    LOADING,
    LOADED,
    NOT_FOUND,
    ERROR,
}

export const PDFPage = () => {
    const { name } = useParams<{ name: string }>();

    const [viewState, setViewState] = useState<ViewState>(ViewState.LOADING);

    const [doc, setDocument] = useState<PDFDocumentProxy>();
    const [progress, setProgress] = useState(0);
    const [pages, setPages] = useState<PDFPageInfo[]>();
    const [pdfAnnotations, setPdfAnnotations] = useState<PdfAnnotations>(new PdfAnnotations([]));
    const [selectedAnnotations, setSelectedAnnotations] = useState<Annotation[]>([]);

    const [pdfsStatuses, setPdfsStatuses] = useState<PdfStatus[]>([]);
    const [activeLabel, setActiveLabel] = useState<Label>({
        name: 'a',
        color: '#FFFFFF',
        metadata: '',
    });
    const [labels, setLabels] = useState<Label[]>([]);
    const [hideLabels, setHideLabels] = useState<boolean>(false);

    const { activeTask, activeDataset } = useContext(DatasetsStore);

    // React's Error Boundaries don't work for us because a lot of work is done by pdfjs in
    // a background task (a web worker). We instead setup a top level error handler that's
    // passed around as needed so we can display a nice error to the user when something
    // goes wrong.
    //
    // We have to use the `useCallback` hook here so that equality checks in child components
    // don't trigger unintentional rerenders.
    const onError = useCallback(
        (err: Error) => {
            console.error('Unexpected Error rendering PDF', err);
            setViewState(ViewState.ERROR);
        },
        [setViewState]
    );

    const theme = useContext(ThemeContext);

    useEffect(() => {
        if (activeTask) {
            getLabels(activeTask).then((labels) => {
                setLabels(labels);
                setActiveLabel(labels[0]);
            });
        }
    }, [activeTask, activeTask]);

    useEffect(() => {
        getPdfsStatues(activeTask, activeDataset).then((pdfsStatuses) => {
            setPdfsStatuses(pdfsStatuses);
        });
    }, [name, activeTask, activeDataset]);

    useEffect(() => {
        setDocument(undefined);
        setViewState(ViewState.LOADING);

        const loadingTask: PDFDocumentLoadingTask = pdfjs.getDocument(pdfURL(name || ''));
        loadingTask.onProgress = (p: { loaded: number; total: number }) => {
            setProgress(Math.round((p.loaded / p.total) * 100));
        };
        Promise.all([
            // PDF.js uses their own `Promise` type, which according to TypeScript doesn't overlap
            // with the base `Promise` interface. To resolve this we (unsafely) cast the PDF.js
            // specific `Promise` back to a generic one. This works, but might have unexpected
            // side-effects, so we should remain wary of this code.
            (loadingTask.promise as unknown) as Promise<PDFDocumentProxy>,
            getTokens(name || ''),
        ])
            .then(([pdfjsDoc, resp]: [PDFDocumentProxy, PagesTokens]) => {
                setDocument(pdfjsDoc);

                // Load all the pages too. In theory this makes things a little slower to startup,
                // as fetching and rendering them asynchronously would make it faster to render the
                // first, visible page. That said it makes the code simpler, so we're ok with it for
                // now.
                const loadPages: Promise<PDFPageInfo>[] = [];
                for (let i = 1; i <= pdfjsDoc.numPages; i++) {
                    // See line 50 for an explanation of the cast here.
                    loadPages.push(
                        (pdfjsDoc.getPage(i).then((pdfjsPage) => {
                            const pageIndex = pdfjsPage.pageNumber - 1;
                            const pageTokens = resp.pages[pageIndex]
                                ? resp.pages[pageIndex].tokens
                                : [];
                            return new PDFPageInfo(pdfjsPage, pageTokens);
                        }) as unknown) as Promise<PDFPageInfo>
                    );
                }
                return Promise.all(loadPages);
            })
            .then((pages) => {
                setPages(pages);
                getAnnotations(activeTask, activeDataset, name || '')
                    .then((paperAnnotations) => {
                        setPdfAnnotations(paperAnnotations);

                        setViewState(ViewState.LOADED);
                    })
                    .catch((err: any) => {
                        console.error(`Error Fetching Existing Annotations: `, err);
                        setViewState(ViewState.ERROR);
                    });
            })
            .catch((err: any) => {
                if (err instanceof Error) {
                    // We have to use the message because minification in production obfuscates
                    // the error name.
                    if (err.message === 'Request failed with status code 404') {
                        setViewState(ViewState.NOT_FOUND);
                        return;
                    }
                }
                console.error(`Error Loading PDF: `, err);
                setViewState(ViewState.ERROR);
            });
    }, [name]);

    const sidebarWidth = '400px';
    switch (viewState) {
        case ViewState.LOADING:
            return (
                <WithSidebar width={sidebarWidth}>
                    <SidebarContainer width={sidebarWidth}>
                        <Tasks />
                        <Datasets />
                        <Pdfs pdfsStatuses={pdfsStatuses} />
                    </SidebarContainer>
                    <CenterOnPage>
                        <Progress
                            type="circle"
                            percent={progress}
                            strokeColor={{ '0%': theme.color.T6, '100%': theme.color.G6 }}
                        />
                    </CenterOnPage>
                </WithSidebar>
            );
        case ViewState.NOT_FOUND:
            return (
                <WithSidebar width={sidebarWidth}>
                    <SidebarContainer width={sidebarWidth}>
                        <Tasks />
                        <Datasets />
                        <Pdfs pdfsStatuses={pdfsStatuses} />
                    </SidebarContainer>
                    <CenterOnPage>
                        <Result icon={<QuestionCircleOutlined />} title="PDF Not Found" />
                    </CenterOnPage>
                </WithSidebar>
            );
        case ViewState.LOADED:
            if (doc && pages && pdfAnnotations) {
                return (
                    <PDFStore.Provider
                        value={{
                            doc,
                            pages,
                            onError,
                        }}>
                        <AnnotationStore.Provider
                            value={{
                                labels,
                                activeLabel,
                                setActiveLabel,
                                pdfAnnotations,
                                setPdfAnnotations,
                                selectedAnnotations,
                                setSelectedAnnotations,
                                hideLabels,
                                setHideLabels,
                            }}>
                            <listeners.UndoAnnotation />
                            <listeners.SaveWithTimeout name={name || ''} />
                            <listeners.HideAnnotationLabels />
                            <WithSidebar width={sidebarWidth}>
                                <SidebarContainer width={sidebarWidth}>
                                    <Tasks />
                                    <Datasets />
                                    {activeTask !== TASKS.reading_order && <Labels />}
                                    <Pdfs pdfsStatuses={pdfsStatuses} />
                                    <Annotations
                                        annotations={pdfAnnotations.annotations}
                                        pdfsStatuses={pdfsStatuses}
                                    />
                                    <Options />
                                </SidebarContainer>
                                <PDFContainer>
                                    <PDF />
                                </PDFContainer>
                            </WithSidebar>
                        </AnnotationStore.Provider>
                    </PDFStore.Provider>
                );
            } else {
                return <div> hi </div>;
            }
        // eslint-disable-line: no-fallthrough
        case ViewState.ERROR:
            return (
                <WithSidebar width={sidebarWidth}>
                    <SidebarContainer width={sidebarWidth}>
                        <Tasks />
                        <Datasets />
                        <Options />
                        {activeTask !== TASKS.reading_order && <Labels />}
                        <Pdfs pdfsStatuses={pdfsStatuses} />
                    </SidebarContainer>
                    <CenterOnPage>
                        <Result status="warning" title="Unable to Render Document" />
                    </CenterOnPage>
                </WithSidebar>
            );
    }
};

interface HasWidth {
    width: string;
}

const WithSidebar = styled.div<HasWidth>(
    ({ width }) => `
    display: grid;
    flex-grow: 1;
    grid-template-columns: minmax(0, 1fr);
    padding-left: ${width};
`
);

const PDFContainer = styled.div(
    ({ theme }) => `
    background: ${theme.color.N4};
    padding: ${theme.spacing.sm};
`
);
