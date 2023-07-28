/**
 * This is the top-level component that defines your UI application.
 *
 * This is an appropriate spot for application wide components and configuration,
 * stuff like application chrome (headers, footers, navigation, etc), routing
 * (what urls go where), etc.
 *
 * @see https://github.com/reactjs/react-router-tutorial/tree/master/lessons
 */

import React, { useEffect, useState } from 'react';
import { createGlobalStyle } from 'styled-components';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { PDFPage } from './pages';
import { getDatasets, getActiveDataset, getActiveTask } from './api';
import { OptionsStore, READING_ORDER, SHOW_TOKENS } from './context/OptionsStore';
import { DatasetsStore } from './context/DatasetsStore';
import { RedirectToFirstPaper } from './RedirectToFirstPaper';

const App = () => {
    const [datasets, setDatasets] = useState<string[]>([]);
    const [activeDataset, setActiveDataset] = useState<string>('');
    const [activeTask, setActiveTask] = useState<string>('');

    const [options, setOptions] = useState<{ [key: string]: boolean }>({
        [READING_ORDER]: false,
        [SHOW_TOKENS]: false,
    });

    useEffect(() => {
        getActiveTask().then((task) => {
            setActiveTask(task);

            getDatasets(task).then((realDatasets) => {
                setDatasets(realDatasets);

                getActiveDataset().then((dataset) => {
                    setActiveDataset(dataset);
                });
            });
        });
    }, []);

    return (
        <OptionsStore.Provider
            value={{
                options,
                setOptions,
            }}>
            <DatasetsStore.Provider
                value={{
                    datasets,
                    setDatasets,
                    activeTask,
                    setActiveTask,
                    setActiveDataset,
                    activeDataset,
                }}>
                <BrowserRouter>
                    <Routes>
                        <Route
                            path="/"
                            element={
                                <>
                                    {activeTask && activeDataset && (
                                        <RedirectToFirstPaper
                                            activeTask={activeTask}
                                            activeDataset={activeDataset}
                                        />
                                    )}
                                </>
                            }></Route>
                        <Route
                            path="/pdf/:name"
                            element={<>{activeTask && activeDataset && <PDFPage />}</>}></Route>
                    </Routes>
                </BrowserRouter>
                <GlobalStyles />
            </DatasetsStore.Provider>
        </OptionsStore.Provider>
    );
};

// Setup the viewport so it takes up all available real-estate.
const GlobalStyles = createGlobalStyle`
  html, body, #root {
    display: flex;
    flex-grow: 1;
  }
`;

export default App;
