import React, { useContext, useEffect, useState } from 'react';
import styled from 'styled-components';
import { SidebarItem, SidebarItemTitle } from './common';
import { Switch, notification } from '@allenai/varnish';
import { Annotation, DatasetsStore, TASKS } from '../../context';

import { CheckOutlined, CloseOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { AnnotationSummary } from '../AnnotationSummary';
import { getTokens, PagesTokens, PdfStatus, setPdfFinished, setPdfJunk } from '../../api';
import { useNavigate, useParams } from 'react-router-dom';

interface AnnotationsProps {
    annotations: Annotation[];
    pdfsStatuses: PdfStatus[];
}

export const Annotations = ({ annotations, pdfsStatuses }: AnnotationsProps) => {
    const { activeTask, activeDataset } = useContext(DatasetsStore);
    const [pageTokens, setPageTokens] = useState<PagesTokens>();

    const navigate = useNavigate();
    const { name } = useParams<{ name: string }>();

    const currentPaperStatus = pdfsStatuses.filter((x) => x.name === name);

    const isFinished =
        currentPaperStatus && currentPaperStatus[0] ? currentPaperStatus[0].finished : false;
    const isJunk = currentPaperStatus && currentPaperStatus[0] ? currentPaperStatus[0].junk : false;

    useEffect(() => {
        const onKeyPress = async (e: KeyboardEvent) => {
            if (e.key === 'e') {
                await setPdfFinished(activeTask, activeDataset, name || '', true);
                notification.success({ message: 'Marked paper as Finished!' });
                navigate('/');
            }
        };

        window.addEventListener('keydown', onKeyPress);
        return () => {
            window.removeEventListener('keydown', onKeyPress);
        };
    });

    useEffect(() => {
        getTokens(name || '').then((pageTokens) => {
            setPageTokens(pageTokens);
        });
    }, [name]);

    const onFinishToggle = async (isFinished: boolean) => {
        await setPdfFinished(activeTask, activeDataset, name || '', isFinished);
        if (isFinished) {
            notification.success({ message: 'Marked paper as Finished!' });
        } else {
            notification.info({ message: 'Marked paper as In Progress.' });
        }
        navigate(0);
    };

    const onJunkToggle = async (isJunk: boolean) => {
        await setPdfJunk(activeTask, activeDataset, name || '', isJunk).then(() => {
            if (isJunk) {
                notification.warning({ message: 'Marked paper as Junk!' });
                navigate('/');
            } else {
                notification.info({ message: 'Marked paper as In Progress.' });
            }
        });

        navigate(0);
    };

    const annotationSort = (a: Annotation, b: Annotation) => {
        if (a.page !== b.page) {
            return a.page - b.page; // Sort by "field1" in ascending order
        } else {
            return a.bounds.top - b.bounds.top; // Sort by "field2" in descending order
        }
    };

    return (
        <SidebarItem>
            <SidebarItemTitle>Annotations</SidebarItemTitle>
            <ExplainerText>
                <InfoCircleOutlined style={{ marginRight: '3px' }} />
                Press "e" key to mark PDF as finished.
            </ExplainerText>
            {activeTask !== TASKS.reading_order && (
                <ExplainerText>
                    <InfoCircleOutlined style={{ marginRight: '3px' }} />
                    Use CMD + z to undo the last annotation.
                </ExplainerText>
            )}
            {activeTask !== TASKS.reading_order && (
                <ExplainerText>
                    <InfoCircleOutlined style={{ marginRight: '3px' }} />
                    Press CTRL to show/hide annotation labels for small annotations.
                </ExplainerText>
            )}
            <span>
                <ToggleDescription>Finished?</ToggleDescription>
                <Toggle
                    checked={isFinished}
                    size="small"
                    onChange={(e) => onFinishToggle(e)}
                    checkedChildren={<CheckOutlined />}
                    unCheckedChildren={<CloseOutlined />}
                />
            </span>
            <span>
                <ToggleDescription>Junk</ToggleDescription>
                <Toggle
                    checked={isJunk}
                    size="small"
                    onChange={(e) => onJunkToggle(e)}
                    checkedChildren={<CheckOutlined />}
                    unCheckedChildren={<CloseOutlined />}
                />
            </span>
            {activeTask !== TASKS.reading_order && (
                <div>
                    {annotations.length === 0 ? (
                        <>No Annotations Yet :(</>
                    ) : (
                        <div>
                            {annotations.sort(annotationSort).map((annotation) => (
                                <AnnotationSummary
                                    key={annotation.id}
                                    annotation={annotation}
                                    pageTokens={pageTokens}
                                />
                            ))}
                        </div>
                    )}
                </div>
            )}
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

const Toggle = styled(Switch)`
    margin: 8px 8px;
`;
const ToggleDescription = styled.span`
    font-size: 0.85rem;
    color: ${({ theme }) => theme.color.N6};
`;
