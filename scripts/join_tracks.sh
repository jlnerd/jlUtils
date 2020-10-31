#!/usr/bin/env bash

set -e

python -m fuegodata.turitag.results.pipelines.join_tracks --job_name=$1