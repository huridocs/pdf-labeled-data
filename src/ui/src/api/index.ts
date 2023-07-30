import axios from 'axios';
import { Annotation, PdfAnnotations } from '../context';

export interface Token {
    x: number;
    y: number;
    height: number;
    width: number;
    text: string;
}

interface Page {
    index: number;
    width: number;
    height: number;
    tokens: Token[];
}

export interface PagesTokens {
    pages: Page[];
}

export function pdfURL(name: string): string {
    return `/api/pdf/${name}`;
}
export async function getDatasets(task: string): Promise<string[]> {
    return axios.get(`/api/annotation/real_datasets/${task}`).then((r) => r.data);
}

export async function getActiveTask(): Promise<string> {
    return axios.get(`/api/annotation/real_active_task`).then((r) => r.data);
}

export async function getActiveDataset(): Promise<string> {
    return axios.get(`/api/annotation/real_active_dataset`).then((r) => r.data);
}

export async function saveActiveDatasets(task: string, dataset: string): Promise<string[]> {
    return axios.post(`/api/annotation/real_active_dataset/${task}/${dataset}`);
}

export function setReadingOrderMultipleAnnotations(
    task: string,
    sha: string,
    annotation: Annotation
): Promise<PdfAnnotations> {
    return axios
        .post(`/api/annotation/reading_order/${task}/${sha}`, annotation)
        .then((response) => {
            const ann: PdfAnnotations = response.data;
            const annotations = ann.annotations.map((a) => Annotation.fromObject(a));

            return new PdfAnnotations(annotations);
        });
}

export function setReadingOrderOneAnnotation(
    task: string,
    sha: string,
    annotation: Annotation,
    label: string
): Promise<PdfAnnotations> {
    return axios
        .post(`/api/annotation/reading_order/${task}/${sha}/${label}`, annotation)
        .then((response) => {
            const ann: PdfAnnotations = response.data;
            const annotations = ann.annotations.map((a) => Annotation.fromObject(a));

            return new PdfAnnotations(annotations);
        });
}

export async function getTokens(name: string): Promise<PagesTokens> {
    return axios.get(`/api/pdf/${name}/tokens`).then((r) => r.data);
}

export interface Label {
    text: string;
    color: string;
}
export async function getLabels(task: string): Promise<Label[]> {
    return axios.get(`/api/annotation/${task}/labels`).then((r) => r.data);
}

export interface PdfStatus {
    sha: string;
    name: string;
    finished: boolean;
    junk: boolean;
}

export async function setPdfFinished(
    task: string,
    dataset: string,
    name: string,
    finished: boolean
) {
    return axios.post(`/api/doc/${task}/${dataset}/${name}/finished/${finished}`);
}

export async function setPdfJunk(task: string, dataset: string, name: string, junk: boolean) {
    return axios.post(`/api/doc/${task}/${dataset}/${name}/junk/${junk}`);
}

export async function deletePdfJunk(task: string, dataset: string, name: string) {
    return axios.post(`/api/pdf/${task}/${dataset}/${name}/delete`);
}

export async function deleteAllJunk(task: string, dataset: string) {
    return axios.post(`/api/pdfs/${task}/${dataset}/delete/all/junk`);
}

export async function getPdfsStatues(task: string, dataset: string): Promise<PdfStatus[]> {
    return axios.get(`/api/annotation/get_pdfs_statuses/${task}/${dataset}`).then((r) => r.data);
}

export function saveAnnotations(
    task: string,
    dataset: string,
    name: string,
    pdfAnnotations: PdfAnnotations
): Promise<any> {
    return axios.post(`/api/doc/${task}/${dataset}/${name}/annotations`, {
        annotations: pdfAnnotations.annotations,
    });
}

export async function getAnnotations(
    task: string,
    dataset: string,
    name: string
): Promise<PdfAnnotations> {
    return axios.get(`/api/pdf/${task}/${dataset}/${name}/annotations`).then((response) => {
        const pdfAnnotations: PdfAnnotations = response.data;
        const annotations = pdfAnnotations.annotations.map((a) => Annotation.fromObject(a));
        return new PdfAnnotations(annotations);
    });
}
