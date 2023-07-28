import React, { useEffect, useMemo, useState } from 'react';
import { getPdfsStatues, PdfStatus } from './api';
import { CenterOnPage } from './components';
import { Result, Spin } from '@allenai/varnish';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { Navigate } from 'react-router-dom';

export const getPdfPath = (pdfsStatuses: PdfStatus[]) => {
    const namePdf = pdfsStatuses.find((p) => !!p.name && !p.finished && !p.junk);
    const namePdfFinished = pdfsStatuses.filter((p) => p.finished).find((p) => !!p.name);
    const namePdfJunk = pdfsStatuses.filter((p) => p.junk).find((p) => !!p.name);

    return namePdf
        ? namePdf.name
        : namePdfFinished
        ? namePdfFinished.name
        : namePdfJunk
        ? namePdfJunk.name
        : undefined;
};

export const RedirectToFirstPaper = (props: { activeTask: string; activeDataset: string }) => {
    const { activeTask, activeDataset } = props;

    const [pdfsStatuses, setPdfsStatuses] = useState<PdfStatus[] | null>(null);

    useEffect(() => {
        getPdfsStatues(activeTask, activeDataset).then((pdfsStatuses) =>
            setPdfsStatuses(pdfsStatuses || [])
        );
    }, []);

    return useMemo(() => {
        if (!pdfsStatuses) {
            return (
                <>
                    <CenterOnPage>
                        <Spin size="large" />
                    </CenterOnPage>
                </>
            );
        }

        const name = getPdfPath(pdfsStatuses);

        if (!name) {
            return (
                <>
                    <CenterOnPage>
                        <Result icon={<QuestionCircleOutlined />} title="PDFs Not Found" />
                    </CenterOnPage>
                </>
            );
        }

        return (
            <>
                <Navigate replace to={`/pdf/${name}`} />
            </>
        );
    }, [pdfsStatuses]);
};
