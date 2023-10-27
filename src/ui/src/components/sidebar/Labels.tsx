import React, { useContext, useEffect } from 'react';
import styled from 'styled-components';
import { Tag, notification } from '@allenai/varnish';

import { AnnotationStore } from '../../context';
import { InfoCircleOutlined } from '@ant-design/icons';

import { SidebarItem, SidebarItemTitle } from './common';

const { CheckableTag } = Tag;

export const Labels = () => {
    const annotationStore = useContext(AnnotationStore);

    useEffect(() => {
        const onKeyPress = (e: KeyboardEvent) => {
            // Numeric keys 1-9
            if (['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'].includes(e.key)) {
                const index = Number.parseInt(e.key) - 1;
                if (index < annotationStore.labels.length) {
                    annotationStore.setActiveLabel(annotationStore.labels[index]);
                }
            }

            // Left/Right Arrow keys
            if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'a' || e.key === 'd') {
                if (!annotationStore.activeLabel) {
                    annotationStore.setActiveLabel(annotationStore.labels[0]);
                    notification.info({ message: `Label ${annotationStore.labels[0].name}` });
                    return;
                }
                const currentIndex = annotationStore.labels.indexOf(annotationStore.activeLabel);
                // Right goes forward
                let next =
                    currentIndex === annotationStore.labels.length - 1 ? 0 : currentIndex + 1;
                // Left goes backward
                if (e.key === 'ArrowLeft' || e.key === 'a') {
                    next =
                        currentIndex === 0 ? annotationStore.labels.length - 1 : currentIndex - 1;
                }
                annotationStore.setActiveLabel(annotationStore.labels[next]);
                notification.info({ message: `Label ${annotationStore.labels[next].name}` });
            }
        };
        window.addEventListener('keydown', onKeyPress);
        return () => {
            window.removeEventListener('keydown', onKeyPress);
        };
    }, [annotationStore]);

    return (
        <SidebarItem>
            <SidebarItemTitle>Labels</SidebarItemTitle>
            <ExplainerText>
                <InfoCircleOutlined style={{ marginRight: '3px' }} />
                Use arrow keys or "a" and "d" keys to select labels to annotate.
            </ExplainerText>
            <Container>
                <div>
                    {annotationStore.labels.map((label) => (
                        <LabelTag
                            key={label.name}
                            onClick={() => {
                                annotationStore.setActiveLabel(label);
                            }}
                            checked={label === annotationStore.activeLabel}
                            style={{ color: label.color }}>
                            {label.name}
                        </LabelTag>
                    ))}
                </div>
            </Container>
        </SidebarItem>
    );
};

const ExplainerText = styled.div`
    font-size: ${({ theme }) => theme.spacing.sm};

    &,
    & * {
        color: ${({ theme }) => theme.color.N6};
    }
`;

const LabelTag = styled(CheckableTag)`
    &.ant-tag-checkable-checked {
        background-color: #303030;
    }
`;

const Container = styled.div(
    ({ theme }) => `
   margin-top: ${theme.spacing.sm};
   div + div {
       margin-top: ${theme.spacing.sm};
   }

`
);
