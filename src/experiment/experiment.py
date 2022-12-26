import numpy as np
import pandas as pd


class Experiment:
    def __init__(self, analyzer, scanner, parameters, route, output_path):
        self.scanner = scanner
        self.analyzer = analyzer
        self.parameters = parameters

        self.route = route
        self.start_point, self.route_diff = self._route_to_diff(route)

        self.output_path = output_path

    @staticmethod
    def _route_to_diff(route):
        return route, route

    def run(self):
        current_position = self.start_point
        for idx, delta_coord in enumerate(self.route_diff):
            for dim, delta_dim in enumerate(delta_coord):
                self.scanner.move(delta_dim, dim=dim)

            current_position += delta_coord
            res_dict = self.analyzer.get_scattering_parameters(self.parameters)
            res_df = pd.DataFrame(res_dict)

            for dim in range(delta_coord.shape[1]):
                res_df[f'dim_{dim}'] = current_position[idx, dim]

            res_df.to_csv(self.output_path, mode='a', header=False)

    def create_data(self):
        parameters_names = self.parameters.names
        dimensions_num = self.route.shape[1]
        header = [*parameters_names, *dimensions_num]

        pd.DataFrame(columns=header).to_csv(self.output_path)


if __name__ == "__main__":
    # experiment = Experiment(analyzer, scanner, params, route, 'data/exp1/test.csv')
    # experiment.run()

    print(2)
