# Pyra: Automated EM27/SUN Greenhouse Gas Measurement Software

**Documentation: [pyra.esm.ei.tum.de/docs](https://pyra.esm.ei.tum.de/docs)**

**Contributor Guide: [https://pyra.esm.ei.tum.de/docs/contributor-guide/becoming-a-contributor](https://pyra.esm.ei.tum.de/docs/contributor-guide/becoming-a-contributor)**

[![status](https://joss.theoj.org/papers/d47b5197eb098bccfbd27b6a6c441cb4/status.svg)](https://joss.theoj.org/papers/d47b5197eb098bccfbd27b6a6c441cb4)
[![GitHub](https://img.shields.io/github/license/tum-esm/pyra?color=f43f5e&style=flat)](https://github.com/tum-esm/pyra/blob/main/LICENSE.md)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/tum-esm/pyra?display_name=tag&label=latest%20release&color=f43f5e&style=flat)](https://github.com/tum-esm/pyra/releases)
<br/>
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/tum-esm/pyra/test-python-codebase-on-main.yml?branch=main&color=f59e0b&label=python%20tests%20on%20main%20branch&style=flat)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/tum-esm/pyra/test-typescript-codebase-on-main.yml?branch=main&color=f59e0b&label=typescript%20tests%20on%20main%20branch&style=flat)

<br/>

## What is Pyra?

Pyra (name based on [Python](<https://en.wikipedia.org/wiki/Python_(programming_language)>) and [Ra](https://en.wikipedia.org/wiki/Ra)) is a software that automates the operation of [EM27/SUN](https://www.bruker.com/en/products-and-solutions/infrared-and-raman/remote-sensing/em27-sun-solar-absorption-spectrometer.html) measurement setups. Operating EM27/SUN devices requires a lot of human interaction. Pyra makes it possible to autonomously operate these devices 24/7.

Pyra has enabled the [Technical University of Munich](https://www.tum.de/en/) to collect continuous data from 5 stations around the city of Munich since 2019 using [MUCCnet](https://atmosphere.ei.tum.de/). Versions 1 to 3 of Pyra have been experimental tools, improved internally since 2016.

![](packages/docs/static/img/docs/muccnet-image-roof.jpg)

The goal of Pyra version 4 is to make it even more stable, easy to understand and extend, and usable by the broad EM27/SUN community.

The software is licensed under GPLv3 and is open-sourced here, on GitHub (https://github.com/tum-esm/pyra). Whenever using Pyra, please make sure to cite the codebase.
