import React, { useContext } from 'react';
import styled from 'styled-components';
import { Contrast, SidebarItem, SidebarItemTitle } from './common';

import { InfoCircleOutlined } from '@ant-design/icons';
import { Tooltip } from '@allenai/varnish';
import { getPdfsStatues, getDatasets } from '../../api';
import { DatasetsStore } from '../../context/DatasetsStore';
import { useNavigate } from 'react-router-dom';
import { getPdfPath } from '../../RedirectToFirstPaper';

export const Tasks = () => {
    const tasks = ['Token Type', 'Reading Order', 'Paragraph Extraction'];
    const { activeTask, setDatasets, setActiveDataset, setActiveTask } = useContext(DatasetsStore);
    const navigate = useNavigate();

    const changeTask = async (task: string) => {
        setActiveTask(task);
        const datasets = await getDatasets(task);
        setDatasets(datasets);
        setActiveDataset(datasets[0]);
        const pdfsStatuses = await getPdfsStatues(task, datasets[0]);
        const name = getPdfPath(pdfsStatuses);
        navigate(`/pdf/${name}`);
    };

    return (
        <SidebarItem>
            <SidebarItemTitle>Tasks</SidebarItemTitle>
            <ExplainerText>
                <InfoCircleOutlined style={{ marginRight: '3px' }} />
                Pick the task to execute
            </ExplainerText>
            <span>
                {tasks.length !== 0 ? (
                    <>
                        {tasks.map((task) => (
                            <Tooltip
                                key={task}
                                placement="left"
                                trigger={['hover']}
                                overlay={<span>{task}</span>}>
                                <span>
                                    {task === activeTask && (
                                        <PaddedRowSelected>
                                            <Contrast>{task}</Contrast>
                                        </PaddedRowSelected>
                                    )}
                                    {task !== activeTask && (
                                        <PaddedRow onClick={() => changeTask(task)}>
                                            <Contrast>{task}</Contrast>
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
