#!/bin/sh
python wikipedia.py || echo "FAILED TO UPDATE WIKIPEDIA"
python ynmp.py || echo "FAILED TO UPDATE YNMP"
python generate_output_html.py || echo "FAILED TO GENERATE output.html"

