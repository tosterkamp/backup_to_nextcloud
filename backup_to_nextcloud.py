from io import BytesIO
import nc_py_api
import tarfile
import os.path
import argparse
import datetime


def make_tarfile(output_filename, source_dir):
    print("Genrerate tar file")
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    print("Tar file created")


def generate_tag():
    now = datetime.datetime.now()

    if now.day == 0:
        tag_name = "monthly"
    elif now.weekday() == 0:
        tag_name = "weekly"
    else:
        tag_name = "daily"

    print("Generated tag: " + tag_name)
    return tag_name


def save_to_nextcloud(file, nc_url, nc_user, nc_pw, nc_file, tag):
    nc = nc_py_api.Nextcloud(nextcloud_url=nc_url, nc_auth_user=nc_user, nc_auth_pass=nc_pw)
    f = open(file, 'rb')

    print("Upload file to " + nc_file)
    nc_file_id = nc.files.upload_stream(nc_file, f)
    print("Upload finished")

    if tag:
        tag_name = generate_tag()
        nc_tag_id = nc.files.tag_by_name(tag_name)
        print("Set tag: " + tag_name)
        nc.files.assign_tag(file_id=nc_file_id.file_id, tag_id=nc_tag_id.tag_id)


def generate_postfix(postfix):
    now = datetime.datetime.now()
    new_postfix = now.strftime(postfix)
    print("Generated postfix: " + new_postfix)
    return new_postfix


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true', help='Backup a directory instead of a file')
    parser.add_argument('--source', help='File/directory to backup')
    parser.add_argument('--postfix', help='Postfix added to the file in Nextcloud with time format arguments', default='_%Y-%m-%d-%H-%M-%S')
    parser.add_argument('--nc_url', help='Nextcloud URL', required=True)
    parser.add_argument('--nc_user', help='Nextcloud user', required=True)
    parser.add_argument('--nc_pw', help='Nextcloud password', required=True)
    parser.add_argument('--nc_dir', help='Nextcloud directory')
    parser.add_argument('--nc_tag', help='Add daily, weekly or monthly tag to file', action='store_false')
    args = parser.parse_args()

    dest_file_path_name = args.source + generate_postfix(args.postfix)
    if args.nc_dir:
        dest_file_path_name = args.nc_dir + "/" + dest_file_path_name

    if args.d:
        make_tarfile("tmp_" + args.source + ".tar.gz", args.source)
        args.source = "tmp_" + args.source + ".tar.gz"
        print(args.source)
        dest_file_path_name = dest_file_path_name + ".tar.gz"

    save_to_nextcloud(args.source, args.nc_url, args.nc_user, args.nc_pw, dest_file_path_name, args.nc_tag)

    if args.d:
        os.remove(args.source)

    print("Backup " + dest_file_path_name + " created")
    exit(0)
