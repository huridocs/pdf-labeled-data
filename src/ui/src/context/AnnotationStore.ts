import { createContext } from 'react';
import { v4 as uuidv4 } from 'uuid';

import { Bounds, doOverlap } from './PDFStore';
import { Label, Token } from '../api';

export interface TokenId {
    pageIndex: number;
    tokenIndex: number;
}

export class PdfAnnotations {
    constructor(
        public readonly annotations: Annotation[],
        public readonly unsavedChanges: boolean = false
    ) {}

    saved(): PdfAnnotations {
        return new PdfAnnotations(this.annotations, false);
    }

    withNewAnnotation(annotation: Annotation): PdfAnnotations {
        const newAnnotations = this.annotations.filter(
            (a) => annotation.page !== a.page || !doOverlap(a.bounds, annotation.bounds)
        );
        return new PdfAnnotations(newAnnotations.concat([annotation]), true);
    }

    deleteAnnotation(a: Annotation): PdfAnnotations {
        const newAnnotations = this.annotations.filter((ann) => ann.id !== a.id);
        return new PdfAnnotations(newAnnotations, true);
    }

    undoAnnotation(): PdfAnnotations {
        const popped = this.annotations.pop();
        if (!popped) {
            // No annotations, nothing to update
            return this;
        }

        return new PdfAnnotations(this.annotations, true);
    }

    private sort() {
        const sortAnnotations = (a: Annotation, b: Annotation) => {
            if (!a.tokens && !b.tokens) {
                return a.page > b.page ? 1 : -1;
            }

            if (!a.tokens && !!b.tokens) {
                return 1;
            }

            if (!!a.tokens && !b.tokens) {
                return 0;
            }

            if (!a.tokens || !b.tokens) {
                return 1;
            }

            return 100000 * a.tokens[0].pageIndex + a.tokens[0].tokenIndex >
                100000 * b.tokens[0].pageIndex + b.tokens[0].tokenIndex
                ? 1
                : -1;
        };

        const sortedAnnotations = this.annotations.sort(sortAnnotations); // sort somehow
        return new PdfAnnotations(sortedAnnotations, this.unsavedChanges);
    }
}

interface _AnnotationStore {
    labels: Label[];

    setActiveLabel: (label: Label) => void;
    activeLabel?: Label;

    pdfAnnotations: PdfAnnotations;
    setPdfAnnotations: (t: PdfAnnotations) => void;

    selectedAnnotations: Annotation[];
    setSelectedAnnotations: (t: Annotation[]) => void;

    hideLabels: boolean;
    setHideLabels: (state: boolean) => void;
}

export class Annotation {
    public readonly id: string;
    public readonly hideLabel: Boolean;

    constructor(
        public bounds: Bounds,
        public readonly page: number,
        public readonly label: Label,
        public readonly tokens: TokenId[] | null = null,
        id: string | undefined = undefined,
        hideLabel: Boolean = false
    ) {
        this.id = id || uuidv4();
        this.hideLabel = hideLabel;
    }

    toString() {
        return this.id;
    }

    /**
     * Returns a deep copy of the provided Annotation with the applied
     * changes.
     */
    update(delta: Partial<Annotation> = {}) {
        return new Annotation(
            delta.bounds ?? Object.assign({}, this.bounds),
            delta.page ?? this.page,
            delta.label ?? Object.assign({}, this.label),
            delta.tokens ?? this.tokens?.map((t) => Object.assign({}, t)),
            this.id
        );
    }

    contains(token: Token) {
        return doOverlap(this.bounds, {
            left: token.x,
            top: token.y,
            right: token.x + token.width,
            bottom: token.y + token.height,
        });
    }

    static fromObject(obj: Annotation) {
        return new Annotation(obj.bounds, obj.page, obj.label, obj.tokens, obj.id);
    }

    static fromObjectTokens(obj: Annotation, tokens: TokenId[]) {
        return new Annotation(obj.bounds, obj.page, obj.label, tokens, obj.id);
    }

    static toAnnotationSegment(obj: Annotation) {
        return new Annotation(
            obj.bounds,
            obj.page,
            { text: 'segmentation', color: '#eac24c' },
            obj.tokens,
            'segmentation',
            true
        );
    }

    static fromToken(token: Token, pageNumber: number) {
        return new Annotation(
            {
                top: token.y,
                left: token.x,
                bottom: token.y + token.height,
                right: token.x + token.width,
            },
            pageNumber,
            { text: 'segmentation', color: '#eac24c' },
            null,
            'segmentation',
            true
        );
    }
}

export const AnnotationStore = createContext<_AnnotationStore>({
    pdfAnnotations: new PdfAnnotations([], false),
    labels: [],
    setActiveLabel: (_?: Label) => {
        throw new Error('Unimplemented');
    },
    activeLabel: undefined,

    selectedAnnotations: [],
    setSelectedAnnotations: (_?: Annotation[]) => {
        throw new Error('Unimplemented');
    },
    setPdfAnnotations: (_: PdfAnnotations) => {
        throw new Error('Unimplemented');
    },
    hideLabels: false,
    setHideLabels: (_: boolean) => {
        throw new Error('Unimplemented');
    },
});
