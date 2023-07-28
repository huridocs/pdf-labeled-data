import React, { useContext } from 'react';
import styled from 'styled-components';
import { Contrast, SidebarItem, SidebarItemTitle } from './common';

import { InfoCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { Tooltip } from '@allenai/varnish';
import { DatasetsStore } from '../../context/DatasetsStore';
import { saveActiveDatasets } from '../../api';

export const Datasets = () => {
    const { activeTask, datasets, activeDataset, setActiveDataset } = useContext(DatasetsStore);
    const navigate = useNavigate();

    async function changeTask(dataset: string) {
        await saveActiveDatasets(activeTask, dataset);
        setActiveDataset(dataset);
        navigate('/');
    }

    return (
        <SidebarItem>
            <SidebarItemTitle>Datasets</SidebarItemTitle>
            <ExplainerText>
                <InfoCircleOutlined style={{ marginRight: '3px' }} />
                Pick the dataset to label
            </ExplainerText>
            <span>
                {datasets.length !== 0 ? (
                    <>
                        {datasets.map((dataset) => (
                            <Tooltip
                                key={dataset}
                                placement="left"
                                trigger={['hover']}
                                overlay={<span>{dataset}</span>}>
                                <span>
                                    {activeDataset === dataset && (
                                        <PaddedRowSelected>
                                            <Contrast>{dataset}</Contrast>
                                        </PaddedRowSelected>
                                    )}
                                    {activeDataset !== dataset && (
                                        <PaddedRow onClick={() => changeTask(dataset)}>
                                            <Contrast>{dataset}</Contrast>
                                        </PaddedRow>
                                    )}
                                </span>
                            </Tooltip>
                        ))}
                    </>
                ) : (
                    <>No tasks!</>
                )}
            </span>
        </SidebarItem>
    );
};

const ExplainerText = styled.div`
    margin-bottom: 8px;
    font-size: ${({ theme }) => theme.spacing.sm};

    &,
    & * {
        color: ${({ theme }) => theme.color.N6};
    }
`;

const PaddedRow = styled.div`
    cursor: pointer;
    padding: 4px 0;
    display: grid;
    grid-template-columns: minmax(0, 1fr) min-content minmax(20px, min-content);
`;

const PaddedRowSelected = styled.div`
    background-color: #222222;
    padding: 4px 0;
    display: grid;
    grid-template-columns: minmax(0, 1fr) min-content minmax(20px, min-content);
`;
