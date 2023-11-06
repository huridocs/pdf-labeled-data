<h3 align="center">PDF labeled data</h3>
<p align="center">Labeled data for creating machine learning models related to PDF consumption: token types, paragraph extraction, and reading order</p>

## Dependencies
* Docker Desktop 4.25.0 [install link](https://www.docker.com/products/docker-desktop/)

## Quick Start
Start the labeling tool:

    make start

When ready, check out the web here:

     http://localhost:8080

To stop the server:

    make stop


## Labeled data

1. Token Type: Labels each word that appears in a PDF. Check out this repository https://github.com/huridocs/pdf-tokens-type-labeler

2. Reading Order: Sorts the information in a PDF https://github.com/huridocs/pdf-reading-order

3. Paragraph Extraction: Segments a PDF in paragraphs https://github.com/huridocs/pdf_paragraphs_extraction

4. Table Of Content: Extracts the Table Of Content https://github.com/huridocs/pdf_paragraphs_extraction



## About

This is a fork, supported by HURIDOCS, of the Allen AI project PAWLS https://github.com/allenai/pawls
