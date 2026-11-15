from speech_to_text.cuda_libraries import library_paths


def install(root, package_folder, library_folder, names):
    folder = root / package_folder / library_folder
    folder.mkdir(parents=True)
    for name in names:
        (folder / name).write_text("")
    return root / package_folder


def test_linux_libraries_are_found_in_load_order_cublaslt_cublas_then_cudnn(tmp_path):
    dirs = {
        "nvidia.cudnn": install(tmp_path, "cudnn", "lib", ["libcudnn.so.9"]),
        "nvidia.cublas": install(
            tmp_path, "cublas", "lib", ["libcublas.so.12", "libcublasLt.so.12"]
        ),
    }

    names = [path.name for path in library_paths(dirs, "linux")]

    assert names == ["libcublasLt.so.12", "libcublas.so.12", "libcudnn.so.9"]


def test_windows_libraries_are_looked_for_in_bin_with_dll_names(tmp_path):
    dirs = {
        "nvidia.cublas": install(
            tmp_path, "cublas", "bin", ["cublasLt64_12.dll", "cublas64_12.dll"]
        ),
        "nvidia.cudnn": install(tmp_path, "cudnn", "bin", ["cudnn64_9.dll"]),
    }

    names = [path.name for path in library_paths(dirs, "win32")]

    assert names == ["cublasLt64_12.dll", "cublas64_12.dll", "cudnn64_9.dll"]


def test_nothing_is_found_when_the_extra_is_not_installed():
    assert library_paths({}, "linux") == []


def test_only_the_installed_package_is_loaded(tmp_path):
    dirs = {"nvidia.cudnn": install(tmp_path, "cudnn", "lib", ["libcudnn.so.9"])}

    assert [path.name for path in library_paths(dirs, "linux")] == ["libcudnn.so.9"]


def test_library_files_that_are_missing_are_skipped(tmp_path):
    dirs = {"nvidia.cublas": install(tmp_path, "cublas", "lib", ["libcublas.so.12"])}

    assert [path.name for path in library_paths(dirs, "linux")] == ["libcublas.so.12"]
