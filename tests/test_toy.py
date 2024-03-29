from src.project.PAnalyzers import ToySparam, ToyAnalyser
from src.project.PScanners import ToyScanner
from src.project.PPaths import ToyPath
from src.project.PExperiments import ToyExperiment
from src.project.PResults import ToyResults, SQLResults
from src.project.Project import PAnalyzerSignals, PMeasurand, PScannerSignals
import numpy as np
from src.analyzers.rohde_schwarz.rohde_schwarz import RohdeSchwarzAnalyzer
from src.Variable import Setting
from src.scanner.TRIM import TRIMScanner

from pathlib import Path


def test_toy_sparams():
    s_para = ToySparam()
    assert s_para.get_data() is None
    res_data = s_para.measure()
    assert res_data.shape == (1000, 2)
    assert np.array_equal(res_data, s_para.get_data())
    assert s_para.get_measure_names() == ("freq", "S11")


def test_toy_analyser():
    anal = ToyAnalyser(PAnalyzerSignals(), RohdeSchwarzAnalyzer(ip="1.1.1.1", port=9000))
    assert isinstance(anal.get_measurands(), list)  # является ли первый аргумент экземпляром класса второго аргумента
    for measurand in anal.get_measurands():
        assert isinstance(measurand, PMeasurand)


def test_toy_scanner():
    scan = ToyScanner(instrument=TRIMScanner(ip="0.0.0.0", port=9000), signals=PScannerSignals())
    for settings in scan.get_settings():
        assert isinstance(settings, Setting)


def test_toy_paths():
    path = ToyPath("path")
    x_min = 0
    x_max = 1000
    x_points = 4

    y_min = 0
    y_max = 1000
    y_points = 4
    path.set_lims(x_min, x_max, y_min, y_max, x_points, y_points)
    res = path.get_points_ndarray()
    assert np.array_equal(res[0:y_points, 1], np.linspace(y_min, y_max, y_points, dtype=float))
    assert np.array_equal(res[y_points:2 * y_points, 1], np.linspace(y_min, y_max, y_points, dtype=float)[::-1])


def test_toy_experiment(TRIM_Scanner_emulator: TRIMScanner):
    scan = ToyScanner(instrument=TRIM_Scanner_emulator, signals=PScannerSignals())
    path = ToyPath("path")
    s_para = ToySparam()
    experiment = ToyExperiment(scan, "exp1")
    x_min = 0
    x_max = 1000
    x_points = 4

    y_min = 0
    y_max = 1000
    y_points = 4
    path.set_lims(x_min, x_max, y_min, y_max, x_points, y_points)

    experiment.set_path(path)
    experiment.set_measurands([s_para])
    experiment.run()


def test_toy_results():
    np.random.seed(42)

    results = ToyResults("results")

    names = ('x', 'y', 'w')
    res_array = np.random.rand(10, 3)
    results.set_names(names)
    results.set_results(res_array)

    assert (results.get_data() == res_array).all()
    assert results.get_data_names() == names


def test_sql_results():
    np.random.seed(42)

    results = SQLResults("sql_results")

    names = ('z', 'w')
    data = np.array([[1, 2], [2, 4]])
    db_path = Path("test_db.db")

    results.set_db_path(db_path)
    results.set_names(names)

    results.set_db(force_create=True)
    results.connect()

    results.append_data(data)
    data_out = results.get_data()

    data_out_true = np.array(
        [[1, None, None, None, 1.0, 2.0],
         [2, None, None, None, 2.0, 4.0]])

    assert (data_out_true == data_out).all()
