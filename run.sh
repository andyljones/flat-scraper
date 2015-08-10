#!/usr/bin/env bash
cd "${0%/*}"
source activate flat-scraper
python github_uploader.py
source deactivate
