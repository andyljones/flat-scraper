#!/usr/bin/env bash
source $HOME/.profile
cd "${0%/*}"
source activate flat-scraper
python github_uploader.py
source deactivate
