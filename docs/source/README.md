| master-publish | master-prb |
|----------------|------------|
|[![loading...](https://badges.pie.apple.com/badges/rio?p=retailappsatx-fuego-data&s=retailappsatx-fuego-data-master-publish)](https://rio.apple.com/projects/retailappsatx-fuego-data)|[![loading...](https://badges.pie.apple.com/badges/rio?p=retailappsatx-fuego-data&s=retailappsatx-fuego-data-master-prb)](https://rio.apple.com/projects/retailappsatx-fuego-data)|

|qa-publish    |qa-prb    |
|----------------|------------|
|[![loading...](https://badges.pie.apple.com/badges/rio?p=retailappsatx-fuego-data&s=retailappsatx-fuego-data-qa-publish)](https://rio.apple.com/projects/retailappsatx-fuego-data)|[![loading...](https://badges.pie.apple.com/badges/rio?p=retailappsatx-fuego-data&s=retailappsatx-fuego-data-qa-prb)](https://rio.apple.com/projects/retailappsatx-fuego-data)|

| dev-publish.   |  dev-prb   |
|----------------|------------|
|[![loading...](https://badges.pie.apple.com/badges/rio?p=retailappsatx-fuego-data&s=retailappsatx-fuego-data-dev-publish)](https://rio.apple.com/projects/retailappsatx-fuego-data)|[![loading...](https://badges.pie.apple.com/badges/rio?p=retailappsatx-fuego-data&s=retailappsatx-fuego-data-dev-prb)](https://rio.apple.com/projects/retailappsatx-fuego-data)|


# Fuego-Data
Utility repo for processing Fuego training data, file transfers, etc.

## file_transfer 
Scripts for file transfer with S3 namespaces. (TODO)

## training_data
Automated detector/tracker training data preprocessing and postprocessing operations

### Tests
Test Python-based modules:
```pytest tests/ -x```

Test shell scripts (`detection/preprocess`):
```bats tests/test_preprocess.sh ```

### Preprocess Videos For Manual Counting or TuritTag Multi-Object Tracking (MOT) Tagging

1. Go to the `fuego_tagging_public` namespace and `footage` s3 bucket
2. Identify the storeID and cameraID of interest.
3. Decide whether you want to slice up videos for turitag (tag) data or manual counting. If turitag, we will specify the slice `mode` as `tag`. For counting we will specify the slice `mode` as `count`
3. Run `bash scripts/download_slice_upload_videos.sh {storeID} {cameraID} {slice mode (tag or count)}`

The function above is a shortcut to the full python command line call: 
```python -m fuegodata.training_data.pipelines.download_slice_upload_videos --storeID={storeID} --cameraID={cameraID} --slice_mode={slice mode}```
You can inspect the doc-string for this function for more details on the exact steps involved.

For the case of manual counting each hour long raw video will be sliced into clips of approximately 15 minutes long. After executing the function above, the processed videos will automatically uploaded to the `counting` bucket, `1_todo` subdirectory, inside the `fuego_tagging_public` namespace

For turitag MOT tagging, The first 15 minutes of each hour long video is sliced into ~5 sec long clips. After executing the function above, the processed videos will automatically uploaded to the `tracking` bucket, `turitag/assets` subdirectory, inside the `fuego_tagging_public` namespace. The Turitag video annoation plugin works best on smaller videos, thus having each video be less than 5MB in size is ideal. Furthermore, the results need to be playable in QuickTime, as this is generally an indicator that they will also work well in safari, which is where the plugin is hosted.

The filenames for the processed videos following the standard nomenclature: `{storeID}_{cameraID}_%m%d%Y_%H-%M-%SUTC_{slice index}.mp4` (i.e. `R290_1575168_06012020_20-50-00UTC_0.mp4`).

#### Generate static images for detection models annotation
```
cd fuegodata/training_data/detection/preprocess
bash video2img.sh videos2do
```
This will created a directory called `sliced` in `detection/preprocess`. 

Structure of a resulted directory for video `R290_1575168_06012020_20-50-00UTC.mov`:
```
fuegodata/training_data/detection/preprocessing/sliced/
  R290_1575168_06012020_20-50-00UTC/
   |——————images
            └—————— frame0001.jpg
            |—————— ...
            └—————— frame9999.jpg
```

### Postprocess
1. Download files uploaded by taggers from [Box](https://apple.ent.box.com/folder/94008743418) or [McQueen](https://store-test.blobstore.apple.com/detection/3_completed).

2. Create a directory in `fuegodata/training_data/detection` with default name `data/`.

3. Clean up any miscellaneous system files (eg. `__MACOSX` or `.DS_Store`):
```
cd fuegodata/training_data/postprocess
python3 clean.py
```

4. Check for data integrity:
```
python3 test.py
```

5. Gather metadata:
```
python3 analyze.py
```
This creates JPEG files with histograms reporting dataset variety:
- Average number of bounding box per frame (crowded vs empty scenes)
- Hour of the day in central time (ideally covering a full day)
- The total number of frames tagged for the video (too high or too low indicates issues) 

Plots generated based on Oct 2019 - June 2020 labelled training data from `R216_1578240`:
![Example - bounding box counts](https://github.pie.apple.com/RetailAppsATX/Fuego-Data/tree/master/fuegodata/training_data/detection/postprocess/bboxes.jpg)
![Example - Average number of bounding box per frame](https://github.pie.apple.com/RetailAppsATX/Fuego-Data/tree/master/fuegodata/training_data/detection/postprocess/hours.jpg)

## Misc utils
To zip all subdirectories into separate `.zip` files, put all files into a directory {DIR} and use:
```
cd fuegodata/training_data/utils
python zip.py --src {DIR}
```

## Publishing and Using Public Datasets

#### Add a new dataset
1. Identify the public dataset's license.
2. Create a dataset at [Turi Trove](https://turitrove.apple.com/) and wait for ML Legal's approval.
3. Clone this repo and set up. This should install `trove` on your bolt instance. Note that as of now (October 2020) FUSE (which Trove uses for mounting) is not supported with Docker on Simcloud. For our purpose you should call `trove download` instead of `trove mount` on a remote instance.
4. After the ML Legal team has reviewed the dataset, upload the raw files to Trove with `trove upload` and `publish`. Follow instructions on the dataset's webpage.

#### Download a published dataset
To download a published dataset from Trove, use `trove download [trove_uri] [local_dir]`. The `trove_uri` is listed on the published dataset's webpage.