import React, { useContext } from 'react';
import styled from 'styled-components';
import { Contrast, SidebarItem, SidebarItemTitle } from './common';

import { InfoCircleOutlined } from '@ant-design/icons';
import { Tooltip } from '@allenai/varnish';
import { getDatasets, saveActiveDatasets } from '../../api';
import { DatasetsStore, TASKS } from '../../context';
import { useNavigate } from 'react-router-dom';

export const Tasks = () => {
    const { activeTask, setDatasets, setActiveDataset, setActiveTask } = useContext(DatasetsStore);
    const navigate = useNavigate();

    const changeTask = async (task: string) => {
        setActiveTask(task);
        const datasets = await getDatasets(task);
        await saveActiveDatasets(task, datasets[0]);
        setDatasets(datasets);
        setActiveDataset(datasets[0]);
        navigate(`/`);
    };

    const titleCase = (taskKey: string) =>
        taskKey.replace(/^_*(.)|_+(.)/g, (s, c, d) =>
            c ? c.toUpperCase() : ' ' + d.toUpperCase()
        );

    return (
        <SidebarItem>
            <SidebarItemTitle>Tasks</SidebarItemTitle>
            <ExplainerText>
                <InfoCircleOutlined style={{ marginRight: '3px' }} />
                Pick the task to execute
            </ExplainerText>
            <span>
                {Object.keys(TASKS).map((task) => (
                    <Tooltip
                        key={task}
                        placement="left"
                        trigger={['hover']}
                        overlay={<span>{task}</span>}>
                        <span>
                            {task === activeTask && (
                                <PaddedRowSelected>
                                    <Contrast>{titleCase(task)}</Contrast>
                                </PaddedRowSelected>
                            )}
                            {task !== activeTask && (
                                <PaddedRow onClick={() => changeTask(task)}>
                                    <Contrast>{titleCase(task)}</Contrast>
                                </PaddedRow>
                            )}
                        </span>
                    </Tooltip>
                ))}
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
