import React, { MouseEvent, useContext, useEffect, useState } from 'react';
import { Annotation, AnnotationStore, DatasetsStore } from '../context';
import { Modal, Select } from '@allenai/varnish';
import { setReadingOrderOneAnnotation } from '../api';

import { useParams } from 'react-router-dom';

interface ReadingOrderModalProps {
    annotations: Annotation[];
    onHide: () => void;
}

export const ReadingOrderModal = ({ annotations, onHide }: ReadingOrderModalProps) => {
    const [readingOrderPosition, setReadingOrderPosition] = useState<string>('1');
    const { activeDataset } = useContext(DatasetsStore);
    const { selectedAnnotations, setSelectedAnnotations, setPdfAnnotations } = useContext(
        AnnotationStore
    );
    const [readingOrderLabels, setReadingOrderLabels] = useState<string[]>([]);

    const { name: currentName } = useParams<{ name: string }>();

    let typedValue = '';
    // There are onMouseDown listeners on the <canvas> that handle the
    // creation of new annotations. We use this function to prevent that
    // from being triggered when the user engages with other UI elements.
    const onMouseDown = (e: MouseEvent) => {
        e.stopPropagation();
    };

    const changeReadingOrder = async (position: string) => {
        if (!selectedAnnotations) {
            return;
        }
        onHide();
        const orderedAnnotations = await setReadingOrderOneAnnotation(
            activeDataset,
            currentName || '',
            selectedAnnotations[0],
            position || '1'
        );
        setPdfAnnotations(orderedAnnotations);
        setSelectedAnnotations([]);
    };

    useEffect(() => {
        const onKeyPress = async (e: KeyboardEvent) => {
            const possibleValues = annotations.map((a) => a.label.name);

            if (e.key === 'Enter') {
                await changeReadingOrder(typedValue);
                return;
            }

            if (e.key === 'Backspace') {
                typedValue = typedValue.slice(0, -1);
            }

            // Numeric keys 1-9
            if (/^[0-9]$/i.test(e.key)) {
                typedValue += e.key;
            }

            if (possibleValues.includes(typedValue)) {
                setReadingOrderPosition(typedValue);
                return;
            }
            typedValue = '';
        };
        window.addEventListener('keydown', onKeyPress);
        return () => {
            window.removeEventListener('keydown', onKeyPress);
        };
    }, [annotations]);

    useEffect(() => {
        const newReadingOrderLabels: string[] = annotations
            .map((annotation) => annotation.label.name)
            .sort((a, b) => {
                return parseInt(a) > parseInt(b) ? 1 : -1;
            })
            .reduce(function (acc: string[], curr) {
                if (!acc.includes(curr)) {
                    acc.push(curr);
                }
                return acc;
            }, []);
        setReadingOrderLabels(newReadingOrderLabels);
    }, [annotations]);

    return (
        <Modal
            title="Reading order position"
            onCancel={onHide}
            onOk={() => changeReadingOrder(readingOrderPosition)}
            cancelButtonProps={{ onMouseDown }}
            okButtonProps={{ onMouseDown }}
            visible>
            <Select<string>
                value={readingOrderPosition}
                onMouseDown={onMouseDown}
                onChange={async (e) => {
                    await changeReadingOrder(e);
                }}
                style={{ display: 'block' }}>
                {readingOrderLabels.map((label) => (
                    <Select.Option value={label} key={label}>
                        {label}
                    </Select.Option>
                ))}
            </Select>
        </Modal>
    );
};
