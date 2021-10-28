import os

import fs

from powersimdata.utility import server_setup

blob_fs = fs.open_fs("azblob://besciences@profiles")


def _get_profile_version(_fs, kind):
    """Returns available raw profiles from the give filesystem

    :param fs.base.FS _fs: filesystem instance
    :param str kind: *'demand'*, *'hydro'*, *'solar'* or *'wind'*.
    :return: (*list*) -- available profile version.
    """
    matching = [f for f in _fs.listdir(".") if kind in f]
    return [f.lstrip(f"{kind}_").rstrip(".csv") for f in matching]


class ProfileHelper:
    BASE_URL = "https://besciences.blob.core.windows.net/profiles"

    @staticmethod
    def get_file_components(scenario_info, field_name):
        """Get the file name and relative path for the given profile and
        scenario.

        :param dict scenario_info: metadata for a scenario.
        :param str field_name: the kind of profile.
        :return: (*tuple*) -- file name and list of path components.
        """
        version = scenario_info["base_" + field_name]
        file_name = field_name + "_" + version + ".csv"
        grid_model = scenario_info["grid_model"]
        return file_name, ("raw", grid_model)

    @staticmethod
    def download_file(file_name, from_dir):
        """Download the profile from blob storage at the given path.

        :param str file_name: profile csv.
        :param tuple from_dir: tuple of path components.
        """
        print(f"--> Downloading {file_name} from blob storage.")
        profile_dir = "/".join(from_dir)
        local_fs = fs.open_fs(os.path.join(server_setup.LOCAL_DIR))
        local_fs.makedirs(profile_dir, recreate=True)
        path = fs.path.join(profile_dir, file_name)
        fs.copy.copy_file(blob_fs, path, local_fs, path)

    @staticmethod
    def get_profile_version_cloud(grid_model, kind):
        """Returns available raw profile from blob storage.

        :param str grid_model: grid model.
        :param str kind: *'demand'*, *'hydro'*, *'solar'* or *'wind'*.
        :return: (*list*) -- available profile version.
        """
        bfs = blob_fs.opendir(f"raw/{grid_model}")
        return _get_profile_version(bfs, kind)

    @staticmethod
    def get_profile_version_local(grid_model, kind):
        """Returns available raw profile from local file.

        :param str grid_model: grid model.
        :param str kind: *'demand'*, *'hydro'*, *'solar'* or *'wind'*.
        :return: (*list*) -- available profile version.
        """
        profile_dir = os.path.join(server_setup.LOCAL_DIR, "raw", grid_model)
        lfs = fs.open_fs(profile_dir)
        return _get_profile_version(lfs, kind)
