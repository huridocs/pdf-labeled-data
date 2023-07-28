import React, { useContext } from 'react';
import { Annotation, PDFStore, AnnotationStore } from '../context';
import { Tag } from '@allenai/varnish';
import styled from 'styled-components';
import { DeleteFilled } from '@ant-design/icons';
import { PagesTokens } from '../api';

interface AnnotationSummaryProps {
    annotation: Annotation;
    pageTokens: PagesTokens | undefined;
}

export const AnnotationSummary = ({ annotation, pageTokens }: AnnotationSummaryProps) => {
    const pdfStore = useContext(PDFStore);
    const annotationStore = useContext(AnnotationStore);

    const onDelete = () => {
        annotationStore.setPdfAnnotations(
            annotationStore.pdfAnnotations.deleteAnnotation(annotation)
        );
    };

    if (!pdfStore.pages) {
        return null;
    }

    const pages =
        !pageTokens || !pageTokens.pages
            ? []
            : pageTokens.pages.filter((x) => x.index === annotation.page);

    const text =
        pages && pages[0]
            ? pages[0].tokens
                  .filter((t) => annotation.contains(t))
                  .map((t) => t.text)
                  .join(' ')
            : '';

    return (
        <PaddedRow>
            <Overflow>{text.slice(0, 30)}</Overflow>
            <SmallTag color={annotation.label.color}>{annotation.label.text}</SmallTag>
            <SmallTag color="grey">Page {annotation.page + 1}</SmallTag>
            <DeleteFilled onClick={onDelete} />
        </PaddedRow>
    );
};

const PaddedRow = styled.div`
    padding: 4px 0;
    border-radius: 2px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) min-content min-content min-content;
`;

const SmallTag = styled(Tag)`
    font-size: 0.65rem;
    padding: 2px 2px;
    border-radius: 4px;
    color: black;
    line-height: 1;
`;
const Overflow = styled.span`
    line-height: 1;
    font-size: 0.8rem;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
`;
