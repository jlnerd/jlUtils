#!/usr/bin/env bash
# IMPORTANT
# Before commiting the changes, notebooks need to be cleaned to remove the media
# TODO: This will be in the pre add git hook
for f in ./notebooks/*.ipynb
do
    echo $f
    jupyter nbconvert "$f" --to notebook --ClearOutputPreprocessor.enabled=True --output "$(basename $f)"
done
