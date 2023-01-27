from src.project.PAnalyzers import ToySparam, ToyAnalyser
from src.project.Project import PAnalyzerSignals, PMeasurand
import numpy as np
from src.analyzator.rohde_schwarz.rohde_schwarz import RohdeSchwarzAnalyzer


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
