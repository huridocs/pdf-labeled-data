import React, { useContext, useEffect, useState } from 'react';
import styled from 'styled-components';
import { SidebarItem, SidebarItemTitle, Contrast } from './common';
import { deleteAllJunk, deletePdfJunk, PdfStatus } from '../../api';
import { notification, Tag } from '@allenai/varnish';

import { EditFilled, DeleteFilled, InfoCircleOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { DatasetsStore } from '../../context';

const PdfRow = (props: { pdfStatus: PdfStatus }) => {
    const { pdfStatus } = props;
    const { activeTask, activeDataset } = useContext(DatasetsStore);
    const navigate = useNavigate();

    const { name: currentName } = useParams<{ name: string }>();
    const deletePdf = async () => {
        await deletePdfJunk(activeTask, activeDataset, pdfStatus.name);

        if (currentName === pdfStatus.name) {
            navigate('/');
            return;
        }

        navigate(0);
    };
    const getIcon = (pdfStatus: PdfStatus) => {
        if (pdfStatus.junk) {
            return <DeleteFilled onClick={deletePdf} />;
        } else {
            return null;
        }
    };

    const getStatusColour = (pdfStatus: PdfStatus) => {
        if (pdfStatus.junk) {
            return '#d5a03a';
        }
        if (pdfStatus.finished) {
            return '#1EC28E';
        }

        return '#AEB7C4';
    };

    return (
        <PaddedRow>
            <Contrast key={pdfStatus.name}>
                <a onClick={() => navigate(`/pdf/${pdfStatus.name}`)}>
                    {pdfStatus.name === currentName && <Selected>{pdfStatus.name}</Selected>}
                    {pdfStatus.name !== currentName && pdfStatus.name}
                </a>
            </Contrast>
            <SmallTag color={getStatusColour(pdfStatus)}>
                <DarkEditIcon />
            </SmallTag>
            {getIcon(pdfStatus)}
        </PaddedRow>
    );
};

export const Pdfs = (props: { pdfsStatuses: PdfStatus[] }) => {
    const { pdfsStatuses } = props;
    const { name } = useParams<{ name: string }>();
    const { activeTask, activeDataset } = useContext(DatasetsStore);
    const unfinished = pdfsStatuses.filter((p) => !p.finished && !p.junk);
    const finished = pdfsStatuses.filter((p) => p.finished);
    const junk = pdfsStatuses.filter((p) => p.junk);
    let ordered = unfinished.concat(finished);
    ordered = ordered.concat(junk);
    const [filterPDF, setFilterPDF] = useState('');

    const pdfToShow = ordered;

    const navigate = useNavigate();
    useEffect(() => {
        const onKeyPress = async (e: KeyboardEvent) => {
            if (e.key === 's') {
                const pdfNames = pdfToShow.map((pdfStatus) => pdfStatus.name);
                const indexCurrentPaper = pdfNames.indexOf(name || '');
                if (pdfNames.length === indexCurrentPaper + 1) {
                    notification.info({ message: 'Last PDF' });
                    return;
                }
                navigate(`/pdf/${pdfNames[indexCurrentPaper + 1]}`);
            }
        };

        window.addEventListener('keydown', onKeyPress);
        return () => {
            window.removeEventListener('keydown', onKeyPress);
        };
    });

    async function deleteAllJunkCallback() {
        await deleteAllJunk(activeTask, activeDataset);
        navigate('/');
    }

    return (
        <SidebarItem>
            <SidebarItemTitle>PDFs</SidebarItemTitle>
            <ExplainerText>
                <InfoCircleOutlined style={{ marginRight: '3px' }} />
                Press "s" key to load next PDF.
            </ExplainerText>
            <ExplainerText>
                <InfoCircleOutlined style={{ marginRight: '3px' }} />
                Unfinished:{pdfToShow.filter((x) => !x.finished && !x.junk).length} Total:{' '}
                {pdfToShow.length}
            </ExplainerText>
            <form>
                <FilterInput
                    type="text"
                    name="pdf_filter"
                    placeholder="Filter PDFs"
                    onChange={(event) => setFilterPDF(event.target.value)}
                />
            </form>
            {pdfsStatuses.length !== 0 ? (
                <>
                    {pdfToShow
                        .filter((pdfStatus) => !filterPDF || pdfStatus.name.includes(filterPDF))
                        .map((pdfStatus) => (
                            <PdfRow key={pdfStatus.name} pdfStatus={pdfStatus} />
                        ))}
                    {junk.length > 0 && (
                        <DeleteButton onClick={deleteAllJunkCallback}>
                            Delete all junk PDFs
                        </DeleteButton>
                    )}
                </>
            ) : (
                <>No Pdfs Allocated!</>
            )}
        </SidebarItem>
    );
};

const DarkEditIcon = styled(EditFilled)`
    margin-left: 4px;

    &,
    & * {
        color: ${({ theme }) => theme.color.N9};
    }
`;

const PaddedRow = styled.div`
    padding: 4px 0;
    display: grid;
    grid-template-columns: minmax(0, 1fr) min-content minmax(20px, min-content);
`;

const SmallTag = styled(Tag)`
    font-size: 0.7rem;
    padding: 2px 2px;
    margin-left: 4px;
    border-radius: 4px;
    color: ${({ theme }) => theme.color.N9};
    line-height: 1;
`;

const Selected = styled.span`
    color: #bd84da;
`;

const ExplainerText = styled.div`
    font-size: ${({ theme }) => theme.spacing.sm};

    &,
    & * {
        color: ${({ theme }) => theme.color.N6};
    }
`;

const FilterInput = styled.input`
    background-color: #e7e7e7;
    width: 90%;
    margin-top: 10px;
    margin-bottom: 10px;
    font-size: 0.8em;
    color: black;
    border: none;

    &:focus {
        border: none;
        box-shadow: none;
        outline: none;
    }
`;

const DeleteButton = styled.button`
    background-color: #ca3131;
    width: 100%;
    cursor: pointer;
    color: white;
    border: none;
    margin-top: 10px;
    margin-bottom: 10px;
`;
