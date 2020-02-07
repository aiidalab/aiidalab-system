__all__ = ['is_app_path', 'fmt_data_files_for_setup_cfg']


def is_app_path(path):
    metadata_file = path / 'metadata.json'
    start_py = path / 'start.py'
    start_md = path / 'start.md'
    return metadata_file.is_file() and \
        (start_py.is_file() or start_md.is_file())


def fmt_data_files_for_setup_cfg(data_files):
    yield "[options.data_files]"
    for root, files in data_files:
        if len(files) == 1:
            yield f"{root} = {files[0]}"
        else:
            yield f"{root} ="
            for fn in files:
                yield f"  {fn}"
