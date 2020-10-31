#!/usr/bin/env bash

# Shortcut to fuegodata.training_data.pipelines.download_slice_upload_videos pipeline

set -e

python -m fuegodata.training_data.pipelines.download_slice_upload_videos --storeID=$1 --cameraID=$2 --slice_mode=$3