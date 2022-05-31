"""
Set up boto3 for communications with McQueen buckets.
"""
import os as _os
import boto3 as _boto3
import yaml as _yaml
import botocore as _botocore
import tqdm as _tqdm

import fuegosecrets as _secrets

from fuegodata import paths as _paths
from fuegodata.utils import files as _files
from fuegodata.utils import zipper as _zipper

# test and prod region names
REGION_NAMES = ["store-test", "store-030"]


def fetch_aws_credentials_fpath():
    """
    Fetches the aws credentials filepath defined by
    `{paths.secrets_dir}/aws/credentials`. If the file does not
    exist, the function will call `fuegosecrets.reveal` to attempt
    to reveal the credentials file from the credentials.secret file

    Args: 
        None
    
    Returns:
        aws_credentials_fpath: string. The file path to the aws credentials file
    """

    aws_credentials_fpath = _os.path.join(_paths.secrets_dir, "aws", "credentials.yml")
    _secrets.reveal(verbose=0)

    return aws_credentials_fpath


def fetch_credentials(aws_credentials_fpath=fetch_aws_credentials_fpath()):
    """
    fetch/load the aws credentials as a dictionary
    
    Args:
        aws_credentials_fpath: string. The file path to where the aws credentials
           file are stored
           
    Returns:
        credentials: dictionary of aws credentials
    """

    assert _os.path.isfile(
        aws_credentials_fpath
    ), f"The aws_credentials_fpath: {aws_credentials_fpath} does not exist"

    with open(aws_credentials_fpath, "r") as f:
        credentials = _yaml.load(f, Loader=_yaml.FullLoader)

    return credentials


def fetch_keys(namespace, aws_credentials_fpath=fetch_aws_credentials_fpath()):
    """
    fetch the aws credential keys (aws_access_key_id, aws_secret_access_key) corresponding
    to the specified namespace in the credentials file.
    
    Args:
        namespace: string. the namespace associated with the access keys. 
            Sometimes called the "profile".
        aws_credentials_fpath: string. The file path to where the aws credentials
           file are stored
    Returns:
        aws_access_key_id: string. the aws_access_key_id string associated with the namespace.
        aws_secret_access_key: string. the aws_secret_access_key string associated with the namespace.
    """

    assert namespace != None, "None is not a valid namespace"

    credentials = fetch_credentials(aws_credentials_fpath)

    assert namespace in list(credentials.keys()), " ".join(
        [
            f"Failed to find the namespace {namespace} in the",
            f"credentials file. The available namespaces are: {list(credentials.keys())}",
        ]
    )

    aws_access_key_id = credentials[namespace]["aws_access_key_id"]
    aws_secret_access_key = credentials[namespace]["aws_secret_access_key"]

    return aws_access_key_id, aws_secret_access_key


def client(
    region_names=REGION_NAMES,
    namespace=None,
    aws_credentials_fpath=fetch_aws_credentials_fpath(),
    port="443",
):

    """
    Instantiates a boto3 client object to interact with the s3 blob store.
    
    Args:
        region_names: list of strings. The region names for which the connection will be attempted
            (note: mcqueen-test is 'store-test').
        namespace: string. The namespace of interest. call `fetch_credentials` to see the namespaces
        aws_credentials_fpath: string. The file path to where the aws credentials
           file are stored
        port: str. The port to be used for the connection
            
    Returns:
        s3_client. botocore.client.S3 object on which other operations may be called to interact with the blob store.
    """

    aws_access_key_id, aws_secret_access_key = fetch_keys(
        namespace, aws_credentials_fpath
    )

    _boto3.setup_default_session()

    for i, region_name in enumerate(region_names):
        try:
            endpoint_url = f"https://{region_name}.....:{port}/"

            s3_client = _boto3.client(
                "s3",
                region_name=region_name,
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )

            # Make sure the connection is established
            s3_client.list_buckets()

            break

        except Exception as e:
            if i + 1 == len(region_names):
                raise e
            else:
                pass

    return s3_client


def resource(
    region_names=REGION_NAMES,
    namespace=None,
    aws_credentials_fpath=fetch_aws_credentials_fpath(),
    port="443",
):

    """
    Instantiates a boto3 resource object to interact with the s3 blob store.
    
    Args:
        region_names: list of strings. The region names for which the connection 
            will be attempted
        namespace: string. The namespace of interest. call `fetch_credentials` to 
            see the namespaces
        aws_credentials_fpath: string. The file path to where the aws credentials
           file are stored
        port: str. The port to be used for the connection
        
    Returns:
        s3_resource. botocore.resource.S3 object on which other operations may be called
        to interact with the blob store.
    """

    aws_access_key_id, aws_secret_access_key = fetch_keys(
        namespace, aws_credentials_fpath
    )
    _boto3.setup_default_session()

    for i, region_name in enumerate(region_names):
        try:
            endpoint_url = f"https://{region_name}.....com:{port}/"

            s3_resource = _boto3.resource(
                "s3",
                region_name=region_name,
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )

            # configure xml parser
            def add_xml_header(params, **kwargs):
                params["headers"]["Accept"] = "application/xml"

            client = s3_resource.meta.client
            client.meta.events.unregister("before-sign.s3", _botocore.utils.fix_s3_host)
            client.meta.events.register("before-call.s3.ListObjects", add_xml_header)

            # Make sure the connection is established
            client.list_buckets()

            break

        except Exception as e:
            if i + 1 == len(region_names):
                raise e
            else:
                pass

    return s3_resource


def ClientResource(
    region_names=REGION_NAMES,
    namespace=None,
    aws_credentials_fpath=fetch_aws_credentials_fpath(),
):
    """
    Instantiate an s3 client and rasource.
    
    Args:
        region_names: list of strings. The region names for which the connection 
            will be attempted
        namespace: string. The namespace of interest. call `fetch_credentials` to 
            see the namespaces
        aws_credentials_fpath: string. The file path to where the aws credentials
           file are stored
            
    Returns:
        s3_client: botocore.client.S3 object on which other operations may be
        called to interact with the blob store.

        s3_resource: botocore.resource.S3 object on which other operations may be
        called to interact with the blob store.

    """
    resource_out = resource(region_names, namespace, aws_credentials_fpath)
    client_out = client(region_names, namespace, aws_credentials_fpath)
    return client_out, resource_out


def create_bucket(s3_client, bucket):
    s3_client.create_bucket(Bucket=bucket)


def list_buckets(s3_client):
    """List the buckets for the namespace associated with the s3_client"""

    meta = s3_client.list_buckets()
    buckets = [obj["Name"] for obj in meta["Buckets"]]

    return buckets


def list_objects(s3_resource, s3_bucket):
    """
    fetch a list of the datasets contained in the fuego_data bucket
    """

    objs = [obj.key for obj in s3_resource.Bucket(s3_bucket).objects.all()]
    objs = [obj for obj in objs if len(_os.path.basename(obj)) > 0]

    return objs


def delete_obj(s3_client, s3_bucket, path_obj):
    """
    Delete an object in a bucket.
    
    Args:
        s3_client: botocore.client.S3. The s3_client to be called.
        s3_bucket: string. The bucket where the object is stored.
        path_obj: string. The path to the object to be deleted in the bucket. (i.e. the key).
    Returns:
        None. The object will be deleted.
        
    """
    s3_client.delete_object(Bucket=s3_bucket, Key=path_obj)


def delete_all_objs(s3_resource, s3_client, s3_bucket, verbose=1):
    """
    Delete all the objs in a s3_bucket
    
    Args:
        s3_resource: The s3_resource object to be called.
        s3_client: botocore.client.S3. The s3_client to be called.
        s3_bucket: string. The bucket where the object is stored.
        verbose: print-out verbosity. If >=1, a progress bar will be added.
            If >=1, the object path for each deleted obj will be printed
    Returns:
        deleted_objs: list of strings of deleted objs
    """
    objs = list_objects(s3_resource, s3_bucket)

    if verbose >= 1:
        try:
            _tqdm.tqdm._instances.clear()
        except:
            pass
        pbar = _tqdm.tqdm(objs)

    for obj in objs:
        if verbose >= 1:
            pbar.update()
        if verbose >= 2:
            print(f"deleting obj: {obj}")

        delete_obj(s3_client, s3_bucket, obj)

    if verbose >= 1:
        pbar.close()

    deleted_objs = objs

    return deleted_objs


def download_single_object(
    s3_resource,
    s3_bucket,
    path_obj,
    local_bucket,
    verbose=0,
    unzip=True,
    ignore_missing=False,
):
    """
    Download a single object.

    Args:
        s3_resource: The s3_resource object to be called.
        s3_bucket: string. The s3 bucket of interest.
        path_obj: string. The path to the object in the s3 bucket.
        local_bucket: string. The path to where object will be downloaded.
        verbose: int. print-out verbosity.
        unzip: boolean. Whether or not to unzip the object (if it is a zip file)
            after downloading
        ignore_missing: boolean. Whether or not to ignore missing files which
            are not found (True), or throw an error if a missing file is
            encountered (False)

    Returns:
        local_path_obj: str. The local path to the downloaded obj
    """

    local_bucket = str(local_bucket)

    trys = 0
    data_returned = False
    while (
        data_returned == False or trys <= 2
    ):  # Try pulling data 2 times if download fails

        local_subfolder = _os.path.join(local_bucket, _os.path.dirname(path_obj))
        if verbose >= 2 and trys == 0:
            print("local_subfolder:", local_subfolder)

        local_path_obj = _os.path.join(local_subfolder, _os.path.basename(path_obj))
        if verbose >= 3 and trys == 0:
            print("local_path_obj:", local_path_obj)

        if not _os.path.isdir(local_subfolder):
            _os.makedirs(local_subfolder)

        if verbose >= 1:
            print("\t", path_obj, end="\r")

        trys += 1
        try:
            s3_resource.Bucket(s3_bucket).download_file(path_obj, local_path_obj)
            data_returned = True
        except Exception as e:
            if "max retries" in str(e):
                pass
            elif "Not Found" in str(e):
                if ignore_missing:
                    _warnings.warn(path_obj + " Not Found")
                    break
                else:
                    raise
            else:
                raise
    if data_returned:
        if unzip and ".zip" in local_path_obj:
            local_path_obj = _zipper.unzip_file(local_path_obj)
    else:
        local_path_obj = None

    return local_path_obj


def download_objs(
    s3_resource,
    s3_bucket,
    objs,
    local_bucket,
    unzip=True,
    overwrite=False,
    ignore_missing=False,
):
    """
    Download a multiple objects (`objs`)

    Args:
        s3_resource: The s3_resource object to be called.
        s3_bucket: string. The s3 bucket of interest.
        obj: list of strings. The paths to the objects in the s3 bucket.
        local_bucket: string. The path to where objects will be downloaded.
        verbose: int. print-out verbosity.
        unzip: boolean. Whether or not to unzip the object (if it is a zip file)
            after downloading
        overwrite: boolean. Whether or not to overwrite the existing objects if
            they are already present locally
        ignore_missing: boolean. Whether or not to ignore missing files which
            are not found (True), or throw an error if a missing file is
            encountered (False)

    Returns:
        fpaths: str. The local filepaths paths to the downloaded objs
    """

    try:
        _tqdm.tqdm._instances.clear()
    except:
        pass
    pbar = _tqdm.tqdm(objs)

    fpaths = []
    for obj in objs:

        pbar.update()

        # Check if the track is already in ACI object store, otherwise download the obj
        fpath = _os.path.join(local_bucket, obj)
        if overwrite or _os.path.exists(fpath) == False:

            fpath = download_single_object(
                s3_resource,
                s3_bucket,
                obj,
                local_bucket,
                verbose=0,
                unzip=unzip,
                ignore_missing=ignore_missing,
            )

        if not fpath == None:
            fpaths.append(fpath)

    pbar.close()

    return fpaths


def upload_single_object(s3_client, s3_bucket, local_fpath, bucket_subdir, verbose=0):
    """
    Upload a single object.

    Args:
        s3_client: The s3_client object to be called.
        s3_bucket: string. The s3 bucket of interest.
        local_fpath: The path to where the file of interest is stored.
        bucket_subdir: string. The subdirectory in the bucket where the file will be saved.

    Returns:
        obj: str. The s3 objects paths for the uploaded files

    """
    obj = _os.path.join(bucket_subdir, _os.path.basename(local_fpath))

    if verbose >= 1:
        print("\t", obj, end="\r")

    s3_client.upload_file(Filename=local_fpath, Bucket=s3_bucket, Key=obj)

    return obj


def upload_objs(
    s3_client, s3_bucket, fpaths,
):
    """
    Upload multiple files to the specified `s3_bucket`. Note that each
    filepath should be in a directory or subdirectory matching the `s3_bucket`
    name.

    Args:
        s3_client: The s3_client object to be called.
        s3_bucket: string. The s3 bucket of interest.
        fpaths: list of strings. The paths to where the files of interest are stored.
            Note that each filepath should be in a directory or subdirectory 
            matching the `s3_bucket` name.

    Returns:
        objs: list of strings. The s3 objects paths for the uploaded files
    """

    try:
        _tqdm.tqdm._instances.clear()
    except:
        pass
    pbar = _tqdm.tqdm(fpaths)

    objs = []
    for fpath in fpaths:

        pbar.update()

        assert s3_bucket in fpath, " ".join(
            [
                f"Failed to find the `s3_bucket`: {s3_bucket}",
                f"in the `fpath`:{fpath}.",
                "The obj path in the `s3_bucket` cannot be interpreted",
                "without this information",
            ]
        )

        bucket_subdir = _os.path.dirname(fpath.split(s3_bucket + "/")[-1])

        obj = upload_single_object(
            s3_client, s3_bucket, fpath, bucket_subdir, verbose=0
        )
        objs.append(obj)

    pbar.close()

    return objs


def download_endpoint(
    namespace,
    aws_credentials_fpath=fetch_aws_credentials_fpath(),
    s3_bucket=None,
    local_bucket=None,
    endpoint=None,
    overwrite=False,
    verbose=1,
):
    """
    Download an endpoint (bucket subfolder) to the local_bucket directory.

    Args:
        namespace: string. The namespace of interest. call `fetch_credentials` to see the namespaces
        aws_credentials_fpath: string. The file path to where the aws credentials
           file are stored.

    Returns: None.
    
    """

    if not _os.path.isdir(local_bucket):
        _os.makedirs(local_bucket)

    s3_client, s3_resource = ClientResource(namespace=namespace,)

    if verbose >= 1:
        print(
            f"downloading bucket: {s3_bucket}, endpoint: {endpoint} to local_bucket: {local_bucket}"
        )

    local_files = _files.list_files(local_bucket)
    local_files = [file.replace(local_bucket, "")[1:] for file in local_files]
    s3_objs = list_objects(s3_resource, s3_bucket)
    endpoint_objs = [obj for obj in s3_objs if endpoint in obj]

    if len(endpoint_objs) is 0:
        raise ValueError(f"No endpoint_objs found at {endpoint}")

    if verbose >= 2:
        pbar = _tf.keras.utils.Progbar(len(s3_objs))

    for p, obj in enumerate(endpoint_objs):

        if overwrite:
            download_single_object(s3_resource, s3_bucket, obj, local_bucket, verbose=0)
        elif overwrite is False:
            if obj not in local_files:
                download_single_object(
                    s3_resource, s3_bucket, obj, local_bucket, verbose=0
                )

        if verbose >= 2:
            pbar.update(p + 1)

    if verbose == 1:
        print(f"\t...download complete")


def upload_endpoint(
    namespace=None,
    aws_credentials_fpath=fetch_aws_credentials_fpath(),
    s3_bucket=None,
    local_bucket=None,
    local_endpoint_dir=None,
    overwrite=True,
    verbose=2,
):
    """
    
    Upload a local endpoint directory to the s3_bucket of interest.
    
    Args:
        namespace: string. The namespace of interest. call `fetch_credentials` to 
            see the namespaces
        aws_credentials_fpath: string. The file path to where the aws credentials
           file are stored.
        s3_bucket: string. The s3 bucket of interest.
        local_bucket: string. The path to where objects will be downloaded to and 
            uploaded from.
        local_endpoint_dir: string. The path to the local endpoint of interest which
            will be uploaded.
        overwrite: boolean. Whether or not to overwrite the mcqueen data with the local data.
        verbose: int. print-out verbosity.

    Returns: 
        None
            
    """

    if not _os.path.isdir(local_bucket):
        _os.makedirs(local_bucket)

    s3_client, s3_resource = ClientResource(namespace=namespace,)

    s3_endpoint = local_endpoint_dir.replace(local_bucket, "")
    if s3_endpoint[0] == "/":
        s3_endpoint = s3_endpoint[1:]

    if verbose >= 1:
        print(
            "\n\t".join(
                [
                    f"uploading local_endpoint_dir {local_endpoint_dir}",
                    f"s3_bucket: {s3_bucket}",
                    f"s3_namespace: {namespace}",
                    f"s3_endpoint {s3_endpoint}",
                ]
            )
        )

    local_files = _files.list_files(local_endpoint_dir)
    s3_objs = list_objects(s3_resource, s3_bucket)
    endpoint_objs = [obj for obj in s3_objs if s3_endpoint in obj]

    if len(local_files) is 0:
        raise ValueError(f"No local_files found at {endpoint}")

    if verbose >= 2:
        pbar = _tf.keras.utils.Progbar(len(local_files))

    for p, local_file in enumerate(local_files):

        bucket_subdir = _os.path.dirname(local_file.replace(local_bucket, ""))
        if bucket_subdir[0] == "/":
            bucket_subdir = bucket_subdir[1:]
        obj = _os.path.join(bucket_subdir, _os.path.basename(local_file))

        if overwrite:
            upload_single_object(
                s3_client, s3_bucket, local_file, bucket_subdir, verbose=0
            )
        elif overwrite is False:
            if obj not in s3_objs:
                upload_single_object(
                    s3_client, s3_bucket, local_file, bucket_subdir, verbose=0
                )

        if verbose >= 2:
            pbar.update(p + 1)

    if verbose >= 1:
        print(f"\t...upload complete")
