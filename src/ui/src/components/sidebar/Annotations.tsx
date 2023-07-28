import React, { useContext, useEffect } from 'react';
import styled from 'styled-components';
import { SidebarItem, SidebarItemTitle } from './common';
import { Switch, notification } from '@allenai/varnish';
import { Annotation } from '../../context';

import { CheckOutlined, CloseOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { AnnotationSummary } from '../AnnotationSummary';
import { setPdfJunk, setPdfFinished } from '../../api';
import { DatasetsStore } from '../../context/DatasetsStore';
import { useNavigate } from 'react-router-dom';
import { OptionsStore, READING_ORDER } from '../../context/OptionsStore';

interface AnnotationsProps {
    sha: string;
    annotations: Annotation[];
    papersStatus: PaperStatus[];
}

export const Annotations = ({ sha, annotations, papersStatus }: AnnotationsProps) => {
    const { activeDataset } = useContext(DatasetsStore);
    const { options } = useContext(OptionsStore);
    const navigate = useNavigate();

    const currentPaperStatus = papersStatus.filter((x) => x.sha === sha);

    const isFinished = currentPaperStatus ? currentPaperStatus[0].finished : false;
    const isJunk = currentPaperStatus ? currentPaperStatus[0].junk : false;

    useEffect(() => {
        const onKeyPress = async (e: KeyboardEvent) => {
            if (e.key === 'e') {
                await setPdfFinished(activeDataset, sha, true);
                notification.success({ message: 'Marked paper as Finished!' });
                navigate('/');
            }
        };

        window.addEventListener('keydown', onKeyPress);
        return () => {
            window.removeEventListener('keydown', onKeyPress);
        };
    });

    const onFinishToggle = async (isFinished: boolean) => {
        await setPdfFinished(activeDataset, sha, isFinished).then(() => {
            if (isFinished) {
                notification.success({ message: 'Marked paper as Finished!' });
            } else {
                notification.info({ message: 'Marked paper as In Progress.' });
            }
        });

        navigate(0);
    };

    const onJunkToggle = async (isJunk: boolean) => {
        await setPdfJunk(activeDataset, sha, isJunk).then(() => {
            if (isJunk) {
                notification.warning({ message: 'Marked paper as Junk!' });
                navigate('/');
            } else {
                notification.info({ message: 'Marked paper as In Progress.' });
            }
        });

        navigate(0);
    };

    return (
        <SidebarItem>
            <SidebarItemTitle>Annotations</SidebarItemTitle>
            <ExplainerText>
                <InfoCircleOutlined style={{ marginRight: '3px' }} />
                Press "e" key to mark PDF as finished.
            </ExplainerText>
            {!options[READING_ORDER] && (
                <ExplainerText>
                    <InfoCircleOutlined style={{ marginRight: '3px' }} />
                    Use CMD + z to undo the last annotation.
                </ExplainerText>
            )}
            {!options[READING_ORDER] && (
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
            {!options[READING_ORDER] && (
                <div>
                    {annotations.length === 0 ? (
                        <>No Annotations Yet :(</>
                    ) : (
                        <div>
                            {annotations.map((annotation) => (
                                <AnnotationSummary key={annotation.id} annotation={annotation} />
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
