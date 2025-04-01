import pathlib as pl

import pytest as pt

testdata = [
    ["kit", pl.Path(r"tests/data/kit")],
    ["utw", pl.Path(r"tests/data/utw")],
    ["kul", pl.Path(r"tests/data/kul"),],
    ["jku", pl.Path(r"tests/data/jku"),],
]


@pt.mark.parametrize("institution, file", testdata)
def test_read_institution(institution, file):
    """Test general functionality of read functions."""
    import pandas as pd

    from smc_benchmark.read import read

    data = read(institution, file)

    for exp, spec_dict in data.items():
        assert isinstance(exp, str)
        assert isinstance(spec_dict, dict)
        for name, values in spec_dict.items():
            assert isinstance(name, str)
            assert isinstance(values, list)
            assert all(isinstance(p, pd.DataFrame) for p in values)
