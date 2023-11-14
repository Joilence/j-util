"""
Upload files/dirs from local to Google Drive
"""
import argparse
from pathlib import Path
from typing import Union

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from tqdm import tqdm


def get_folder_id_by_name(
        folder_name: str,
        parent_folder_id: str = 'root',
        create_if_not_exist=True
):
    """ get folder id of a folder in Google Drive
    :param folder_name: name of the folder
    :param parent_folder_id: id of the parent folder, default to root
    :param create_if_not_exist: create the folder if not existed
    :return: folder id
    """
    # check if folder_name exists in parent_folder_id
    file_list = drive.ListFile({'q': f"'{parent_folder_id}' in parents and trashed=false"}).GetList()
    for file in file_list:
        if file['title'] == folder_name:
            return file['id']
    
    if create_if_not_exist:
        tqdm.write(f"Creating folder {folder_name} under {parent_folder_id}")
        folder = drive.CreateFile({'title': folder_name,
                                   'parents': [{'id': parent_folder_id}],
                                   'mimeType': 'application/vnd.google-apps.folder'})
        folder.Upload()
        return folder['id']
    else:
        tqdm.write(f"Folder {folder_name} does not exist in {parent_folder_id}")
        return None


def upload_file_to(parent_folder_id: str, file_path: Union[str, Path]):
    """ upload file to Google Drive; and files with same name are allowed in Google Drive
    :param parent_folder_id: id of the folder
    :param file_path: path of the file
    """
    file_path = Path(file_path)
    file = drive.CreateFile({'title': file_path.name, 'parents': [{'id': parent_folder_id}]})
    file.SetContentFile(file_path.as_posix())
    file.Upload()
    tqdm.write(f"Uploaded {file_path.as_posix()}")


def upload_dir_to(parent_folder_id: str, dir_path: Union[str, Path]):
    """ upload directory and all its files to google drive
    :param parent_folder_id: id of the folder to upload to
    :param dir_path: path of the directory
    """
    dir_path = Path(dir_path)
    dir_id = get_folder_id_by_name(folder_name=dir_path.name,
                                   parent_folder_id=parent_folder_id,
                                   create_if_not_exist=True)
    files_in_dir = list(Path(dir_path).glob("*"))
    for f in tqdm(files_in_dir, desc=f"Uploading {dir_path.as_posix()}", ncols=10, leave=False):
        if f.is_dir():
            upload_dir_to(parent_folder_id=dir_id, dir_path=f)
        else:
            upload_file_to(parent_folder_id=dir_id, file_path=f)
    tqdm.write(f"Uploaded {dir_path.as_posix()}")


# arguments
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--dest_dir_name', type=str, required=True,
                    help='destination directory name in Google Drive root')
parser.add_argument('-p', '--paths', type=str, nargs='+', required=True,
                    help='paths of files/dirs to upload')
args = parser.parse_args()
dest_dir_name = args.dest_dir_name
upload_paths = args.paths

# authenticate
gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
gauth.CommandLineAuth()  # working in SSH without redirect URL
drive = GoogleDrive(gauth)

# get folder id of save_dir
dest_dir_id = get_folder_id_by_name(folder_name=dest_dir_name, create_if_not_exist=True)

upload_paths += [
    # manually add files/dirs to upload
]
for fp in tqdm(upload_paths, desc="Uploading file/dir lists", ncols=15):
    if Path(fp).is_dir():
        upload_dir_to(parent_folder_id=dest_dir_id, dir_path=fp)
    else:
        upload_file_to(parent_folder_id=dest_dir_id, file_path=fp)
