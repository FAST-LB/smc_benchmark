"""Test reading of experimental data."""

import pathlib as pl
import shutil

import pytest as pt

testdata = [
    ["kit", pl.Path(r"tests/data/kit")],
    ["utw", pl.Path(r"tests/data/utw")],
    ["kul", pl.Path(r"tests/data/kul")],
    ["ecn", pl.Path(r"tests/data/ecn")],
    ["rise", pl.Path(r"tests/data/rise")],
    ["tum", pl.Path(r"tests/data/tum")],
    ["uob", pl.Path(r"tests/data/uob")],
    ["wmg", pl.Path(r"tests/data/wmg")],
    ["jku", pl.Path(r"tests/data/jku")],
]


@pt.fixture(scope="session")
def dir_results():
    """Create a results dir."""
    base_path = pl.Path(__file__).resolve().parent
    res_path = base_path / "results"
    if res_path.exists():
        shutil.rmtree(res_path)
    res_path.mkdir()
    return res_path


@pt.mark.parametrize("institution, file", testdata)
def test_read_institution(institution, file):
    """Test general functionality of read functions."""
    import pandas as pd

    from smc_benchmark.read import read

    data = read(institution, file)

    for exp, spec_dict in data.items():
        assert isinstance(exp, str)
        assert isinstance(spec_dict, dict)
        for name, experiments in spec_dict.items():
            assert isinstance(name, str)
            for id_i, df_i in experiments.items():
                assert isinstance(id_i, int)
                assert isinstance(df_i, pd.DataFrame)


@pt.mark.parametrize("institution, file", testdata)
def test_plotting(institution, file, dir_results):
    """Test force-time plotting."""
    import matplotlib.pyplot as plt

    from smc_benchmark._naming import DISPLACEMENT, FORCE
    from smc_benchmark.read import read

    data = read(institution, file)

    path = pl.Path(dir_results)

    # Plot all configurations
    for material, configs in data.items():
        for config, experiments in configs.items():
            _, ax = plt.subplots(1, 1)
            for experiment in experiments.values():
                ax.plot(experiment[DISPLACEMENT], experiment[FORCE])
            ax.set_xlabel("Displacement in mm")
            ax.set_ylabel("Force in N")
            ax.set_title(f"{material} {config}")
            plt.savefig(path / f"{institution}_{material}_{config}.png", dpi=300)
            plt.close()
