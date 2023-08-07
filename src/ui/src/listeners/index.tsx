import { useEffect, useContext } from 'react';
import { AnnotationStore } from '../context';
import { saveAnnotations } from '../api';
import { notification } from '@allenai/varnish';
import { DatasetsStore } from '../context/DatasetsStore';

export const UndoAnnotation = () => {
    const annotationStore = useContext(AnnotationStore);
    const { pdfAnnotations, setPdfAnnotations } = annotationStore;
    useEffect(() => {
        const handleUndo = (e: KeyboardEvent) => {
            if (e.metaKey && e.key === 'z') {
                setPdfAnnotations(pdfAnnotations.undoAnnotation());
            }
        };

        window.addEventListener('keydown', handleUndo);
        return () => {
            window.removeEventListener('keydown', handleUndo);
        };
    }, [pdfAnnotations, setPdfAnnotations]);

    return null;
};

export const HideAnnotationLabels = () => {
    // Shows or hides the labels of annotations on pressing ctrl.
    // This makes it easier to do detailed annotations.

    const annotationStore = useContext(AnnotationStore);
    const { hideLabels, setHideLabels } = annotationStore;

    // Toggle state on key down.
    useEffect(() => {
        const hideLabelsOnKeyDown = (e: KeyboardEvent) => {
            if (e.ctrlKey) {
                setHideLabels(!hideLabels);
            }
        };
        window.addEventListener('keydown', hideLabelsOnKeyDown);
        return () => {
            window.removeEventListener('keydown', hideLabelsOnKeyDown);
        };
    }, [hideLabels, setHideLabels]);

    return null;
};

interface WithName {
    name: string;
}

export const SaveWithTimeout = ({ name }: WithName) => {
    const annotationStore = useContext(AnnotationStore);
    const { activeDataset, activeTask } = useContext(DatasetsStore);

    const { pdfAnnotations, setPdfAnnotations } = annotationStore;

    useEffect(() => {
        // We only save annotations once the annotations have
        // been fetched, because otherwise we save when the
        // annotations and relations are empty.
        if (pdfAnnotations.unsavedChanges) {
            const currentTimeout = setTimeout(() => {
                saveAnnotations(activeTask, activeDataset, name, pdfAnnotations)
                    .then(() => {
                        setPdfAnnotations(pdfAnnotations.saved());
                    })
                    .catch((err) => {
                        notification.error({
                            message: 'Sorry, something went wrong!',
                            description:
                                'Try re-doing your previous annotation, or contact someone on the Semantic Scholar team.',
                        });
                        console.log('Failed to save annotations: ', err);
                    });
            }, 100);
            return () => clearTimeout(currentTimeout);
        }
    }, [name, pdfAnnotations]);

    return null;
};

// TODO(Mark): There is a lot of duplication between these two listeners,
// deduplicate if I need to save at another time as well.

export const SaveBeforeUnload = ({ name }: WithName) => {
    const annotationStore = useContext(AnnotationStore);
    const { activeDataset, activeTask } = useContext(DatasetsStore);

    const { pdfAnnotations, setPdfAnnotations } = annotationStore;
    useEffect(() => {
        const beforeUnload = (e: BeforeUnloadEvent) => {
            e.preventDefault();
            saveAnnotations(activeTask, activeDataset, name, pdfAnnotations)
                .then(() => {
                    setPdfAnnotations(pdfAnnotations.saved());
                })
                .catch((err) => {
                    notification.error({
                        message: 'Sorry, something went wrong!',
                        description: 'Try re-doing your previous annotation.',
                    });
                    console.log('Failed to save annotations: ', err);
                })
                .then(() => window.close());
        };

        window.addEventListener('beforeunload', beforeUnload);
        return () => {
            window.removeEventListener('beforeunload', beforeUnload);
        };
    }, [name, pdfAnnotations]);

    return null;
};
