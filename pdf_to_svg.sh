#!/bin/bash
for pdf in data/*.pdf; do
  inkscape --without-gui --file="$pdf" --export-plain-svg="${pdf%.pdf}.svg"
done

