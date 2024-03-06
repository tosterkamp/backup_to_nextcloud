from io import BytesIO
import nc_py_api
import tarfile
import os.path
import argparse
import datetime


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def save_to_nextcloud(file, nc_url, nc_user, nc_pass, nc_file):
    nc = nc_py_api.Nextcloud(nextcloud_url=nc_url, nc_auth_user=nc_user, nc_auth_pass=nc_pass)
    f = open(file, 'rb')
    nc.files.upload_stream(nc_file, f) 


def generate_filename(name):
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d-%H-%M-%S')

    if now.day == 0:
        period = "monthly"
    elif now.weekday() == 0:
        period = "weekly"
    else:
        period = "daily"

    return name + "_" + timestamp + "_" + period + ".tar.gz"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', help='Directory to backup')
    parser.add_argument('--nc_url', help='Nextcloud URL')
    parser.add_argument('--nc_user', help='Nextcloud user')
    parser.add_argument('--nc_pw', help='Nextcloud password')
    parser.add_argument('--nc_dir', help='Nextcloud directory')
    args = parser.parse_args()

    filename = generate_filename(args.dir)
    make_tarfile(filename, args.dir)
    save_to_nextcloud(filename, args.nc_url, args.nc_user, args.nc_pw, args.nc_dir + "/" + filename)
    os.remove(filename)

    print("Backup " + filename + " created")
    exit(0)
