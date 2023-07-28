import { createContext } from 'react';

interface _DatasetsStore {
    datasets: string[];
    setDatasets: (realDataset: string[]) => void;

    activeTask: string;
    setActiveTask: (task: string) => void;

    activeDataset: string;
    setActiveDataset: (dataset: string) => void;
}

export const DatasetsStore = createContext<_DatasetsStore>({
    datasets: [],
    setDatasets: (_: string[]) => {},

    activeTask: '',
    setActiveTask: (_: string) => {},

    activeDataset: '',
    setActiveDataset: (_: string) => {},
});
