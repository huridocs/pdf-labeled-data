import React, { MouseEvent, useContext, useState } from 'react';
import styled, { ThemeContext } from 'styled-components';
import { Modal, Select } from '@allenai/varnish';

import {
    Bounds,
    TokenId,
    PDFPageInfo,
    Annotation,
    AnnotationStore,
    TASKS,
    OptionsStore,
    HIDE_LABELS_NAMES,
} from '../context';
import { CloseCircleFilled, EditFilled } from '@ant-design/icons';
import { DatasetsStore } from '../context/DatasetsStore';

function hexToRgb(hex: string) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!result) {
        throw new Error('Unable to parse color.');
    }
    return {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
    };
}

function getBorderWidthFromBounds(bounds: Bounds): number {
    //
    const width = bounds.right - bounds.left;
    const height = bounds.bottom - bounds.top;
    if (width < 100 || height < 100) {
        return 1;
    } else {
        return 3;
    }
}

interface SelectionBoundaryProps {
    color: string;
    bounds: Bounds;
    selected: boolean;
    children?: React.ReactNode;
    annotationId?: string;
    onClick?: () => void;
    isMouseSelection: boolean;
}

export const SelectionBoundary = ({
    color,
    bounds,
    children,
    onClick,
    selected,
}: SelectionBoundaryProps) => {
    const width = bounds.right - bounds.left;
    const height = bounds.bottom - bounds.top;
    const rotateY = width < 0 ? -180 : 0;
    const rotateX = height < 0 ? -180 : 0;
    const rgbColor = hexToRgb(color);
    const border = getBorderWidthFromBounds(bounds);

    const selectionHeight = height;
    return (
        <span
            onClick={(e) => {
                // Here we are preventing the default PdfAnnotationsContainer
                // behaviour of drawing a new bounding box if the shift key
                // is pressed in order to allow users to select multiple
                // annotations and associate them together with a relation.
                if (e.shiftKey && onClick) {
                    e.stopPropagation();
                    onClick();
                }
            }}
            onMouseDown={(e) => {
                if (e.shiftKey && onClick) {
                    e.stopPropagation();
                }
            }}
            style={{
                position: 'absolute',
                left: `${bounds.left}px`,
                top: `${bounds.top}px`,
                width: `${Math.abs(width)}px`,
                height: `${Math.abs(selectionHeight)}px`,
                transform: `rotateY(${rotateY}deg) rotateX(${rotateX}deg)`,
                transformOrigin: 'top left',
                border: `${border}px solid ${color}`,
                background: `rgba(${rgbColor.r}, ${rgbColor.g}, ${rgbColor.b}, ${
                    selected ? 0.3 : 0.1
                })`,
            }}>
            {children || null}
        </span>
    );
};

interface TokenSpanProps {
    isSelected?: boolean;
}

const TokenSpan = styled.span<TokenSpanProps>(
    ({ theme, isSelected }) => `
    position: absolute;
    background: ${isSelected ? theme.color.B3 : 'none'};
    opacity: 0.2;
    border-radius: 3px;
`
);

interface SelectionTokenProps {
    pageInfo: PDFPageInfo;
    tokens: TokenId[] | null;
}
export const SelectionTokens = ({ pageInfo, tokens }: SelectionTokenProps) => {
    return (
        <>
            {tokens &&
                tokens.map((t, i) => {
                    const b = pageInfo.getScaledTokenBounds(pageInfo.tokens[t.tokenIndex]);
                    return (
                        <TokenSpan
                            key={i}
                            isSelected={true}
                            style={{
                                left: `${b.left}px`,
                                top: `${b.top}px`,
                                width: `${b.right - b.left}px`,
                                height: `${b.bottom - b.top}px`,
                                // Tokens don't respond to pointerEvents because
                                // they are ontop of the bounding boxes and the canvas,
                                // which do respond to pointer events.
                                pointerEvents: 'none',
                            }}
                        />
                    );
                })}
        </>
    );
};

interface EditLabelModalProps {
    annotation: Annotation;
    onHide: () => void;
}

const EditLabelModal = ({ annotation, onHide }: EditLabelModalProps) => {
    const annotationStore = useContext(AnnotationStore);

    const [selectedLabel, setSelectedLabel] = useState(annotation.label);

    // There are onMouseDown listeners on the <canvas> that handle the
    // creation of new annotations. We use this function to prevent that
    // from being triggered when the user engages with other UI elements.
    const onMouseDown = (e: MouseEvent) => {
        e.stopPropagation();
    };

    return (
        <Modal
            title="Edit Label"
            onCancel={onHide}
            onOk={() => {
                annotationStore.setPdfAnnotations(
                    annotationStore.pdfAnnotations
                        .deleteAnnotation(annotation)
                        .withNewAnnotation(annotation.update({ label: selectedLabel }))
                );
                onHide();
            }}
            cancelButtonProps={{ onMouseDown }}
            okButtonProps={{ onMouseDown }}
            visible>
            <Select<string>
                value={selectedLabel.name}
                onMouseDown={onMouseDown}
                onChange={(labelText) => {
                    const label = annotationStore.labels.find((l) => l.name === labelText);
                    if (!label) {
                        return;
                    }
                    setSelectedLabel(label);
                }}
                style={{ display: 'block' }}>
                {annotationStore.labels.map((l) => (
                    <Select.Option value={l.name} key={l.name}>
                        {l.name}
                    </Select.Option>
                ))}
            </Select>
        </Modal>
    );
};

interface SelectionProps {
    pageInfo: PDFPageInfo;
    annotation: Annotation;
    showInfo?: boolean;
}

export const Selection = ({ pageInfo, annotation, showInfo = true }: SelectionProps) => {
    const label = annotation.label;
    const theme = useContext(ThemeContext);
    const [isEditLabelModalVisible, setIsEditLabelModalVisible] = useState(false);
    const { activeTask } = useContext(DatasetsStore);
    const annotationStore = useContext(AnnotationStore);
    const { options } = useContext(OptionsStore);

    let color;
    if (!label) {
        color = theme.color.N4.hex; // grey as the default.
    } else {
        color = label.color;
    }

    const bounds = pageInfo.getScaledBounds(annotation.bounds);
    const border = getBorderWidthFromBounds(bounds);

    const removeAnnotation = () => {
        annotationStore.setPdfAnnotations(
            annotationStore.pdfAnnotations.deleteAnnotation(annotation)
        );
    };

    const onShiftClick = () => {
        const current = annotationStore.selectedAnnotations.slice(0);

        // Current contains this annotation, so we remove it.
        if (current.some((other) => other.id === annotation.id)) {
            const next = current.filter((other) => other.id !== annotation.id);
            annotationStore.setSelectedAnnotations(next);
            // Otherwise we add it.
        } else {
            current.push(annotation);
            annotationStore.setSelectedAnnotations(current);
        }
    };

    const selected = annotationStore.selectedAnnotations.includes(annotation);

    return (
        <>
            <SelectionBoundary
                color={color}
                bounds={bounds}
                onClick={onShiftClick}
                selected={selected}
                isMouseSelection={false}>
                {showInfo && !annotationStore.hideLabels && !annotation.hideLabel ? (
                    <SelectionInfo border={border} color={color} onClick={onShiftClick}>
                        <span>
                            {!options[HIDE_LABELS_NAMES] && label.name} {label.metadata}
                        </span>
                        {activeTask !== TASKS.reading_order && !options[HIDE_LABELS_NAMES] && (
                            <>
                                <EditFilled
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setIsEditLabelModalVisible(true);
                                    }}
                                    onMouseDown={(e) => {
                                        e.stopPropagation();
                                    }}
                                />
                                <CloseCircleFilled
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        removeAnnotation();
                                    }}
                                    // We have to prevent the default behaviour for
                                    // the pdf canvas here, in order to be able to capture
                                    // the click event.
                                    onMouseDown={(e) => {
                                        e.stopPropagation();
                                    }}
                                />
                            </>
                        )}
                    </SelectionInfo>
                ) : null}
            </SelectionBoundary>
            {
                // NOTE: It's important that the parent element of the tokens
                // is the PDF canvas, because we need their absolute position
                // to be relative to that and not another absolute/relatively
                // positioned element. This is why SelectionTokens are not inside
                // SelectionBoundary.
                annotation.tokens ? (
                    <SelectionTokens pageInfo={pageInfo} tokens={annotation.tokens} />
                ) : null
            }
            {isEditLabelModalVisible && !annotation.hideLabel ? (
                <EditLabelModal
                    annotation={annotation}
                    onHide={() => setIsEditLabelModalVisible(false)}
                />
            ) : null}
        </>
    );
};

// We use transform here because we need to translate the label upward
// to sit on top of the bounds as a function of *its own* height,
// not the height of it's parent.
interface SelectionInfoProps {
    border: number;
    color: string;
}
const SelectionInfo = styled.div<SelectionInfoProps>(
    ({ border, color }) => `
        position: absolute;
        right: -${border}px;
        transform:translateY(-100%);
        border: ${border} solid  ${color};
        background: ${color};
        font-weight: bold;
        font-size: 12px;
        user-select: none;

        * {
            margin: 2px;
            vertical-align: middle;
        }
    `
);
