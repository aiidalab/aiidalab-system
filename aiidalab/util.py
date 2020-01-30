__all__ = ['fmt_data_files_for_setup_cfg']


def fmt_data_files_for_setup_cfg(data_files):
    for root, files in data_files:
        if len(files) == 1:
            yield f"{root} = {files[0]}"
        else:
            yield f"{root} ="
            for fn in files:
                yield f"  {fn}"
