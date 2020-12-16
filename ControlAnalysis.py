import pandas as pd
import math
import datetime
from copy import deepcopy
from itertools import product


def flatten_tuple(t):
    """
    convert ((a, b, c...), A) to [a, b, c, ..., A]
    :param t:
    :return:
    """
    return [_i for _i in t[0] if isinstance(t[0], tuple)] + [t[1]]


class ControlAnalysis:
    def __init__(self):
        pass

    def control_direction_explore(self, data, condition_columns, condition_tolerance, control_columns,
                                  objective_column, ascending, min_points):
        """
        generate graphs indicating better control direction based on limited data
        :param data: dataframe
        :param condition_columns: list including key condition column names that defines a unique condition
        :param condition_tolerance: list of values showing tolerance bin size for corresponding condition columns.
        :param control_columns: list including control parameters that can be adjusted
        :param objective_column: str, column name
        :param ascending: bool, True represents higher the objective value, better the control is, vice versa.
        :param min_points: int, minimum data points in one bin to do analysis
        :return: dataframe or charts # todo
        """
        # todo: give tolerance option for each condition. for now keep using min and max points
        data_tmp = deepcopy(data)
        # separate conditions
        cut_level = []
        for _i in range(len(condition_columns)):
            _column = condition_columns[_i]
            _bin_size = condition_tolerance[_i]
            _min = data_tmp[_column].min()
            _max = data_tmp[_column].max()
            _range = [_min + _n * _bin_size for _n in range(0, math.ceil((_max-_min)/_bin_size)+1)]
            data_tmp[_column + "_cut"] = pd.cut(data_tmp[_column], bins=_range)
            cut_level.append(data_tmp[_column + "_cut"].unique())

        # traversal conditions
        if len(condition_columns) == 1:  # todo: maybe optimize?
            traversal = cut_level[0]
        else:
            traversal = list(product(cut_level[0], cut_level[1]))
            for _i in range(2, len(condition_columns)):
                traversal = list(product(traversal, cut_level[_i]))
                traversal = [flatten_tuple(_t) for _t in traversal]
        print(f"total conditions to traverse:{len(traversal)}")

        cut_columns = [_name + "_cut" for _name in condition_columns]
        result = []
        start_time = datetime.datetime.now()
        index_counting = 1
        for _condition in traversal:
            _bin = data_tmp.copy()
            for _i in range(len(cut_columns)):
                _bin = _bin[_bin[cut_columns[_i]] == _condition[_i]]
            print(f"\r>>{index_counting}", end="")
            index_counting += 1

            if len(_bin) < min_points:
                continue
            else:
                _min = _bin[_bin[objective_column] == _bin[objective_column].min()]
                _max = _bin[_bin[objective_column] == _bin[objective_column].max()]
                _bin_result = list(_condition) + [_min[objective_column].min(), _max[objective_column].max()]
                for _controlP in control_columns:
                    _bin_result.append(_min[_controlP].mean())
                    _bin_result.append(_max[_controlP].mean())
                result.append(_bin_result)

        print(f"total traversal time:{datetime.datetime.now() - start_time}")

        result_columns = cut_columns + ["min_objective", "max_objective"] + \
            ["min_" + _name for _name in control_columns] + ["max_" + _name for _name in control_columns]
        result = pd.DataFrame(result, columns = result_columns)
        if ascending:
            new_columns = [_name.replace("min", "before_optimize") for _name in result_columns]
            new_columns = [_name.replace("max", "after_optimize") for _name in new_columns]
            result.columns = new_columns
        else:
            new_columns = [_name.replace("max", "before_optimize") for _name in result_columns]
            new_columns = [_name.replace("min", "after_optimize") for _name in new_columns]
            result.columns = new_columns
        result["objective_change_percent"] = \
            (result["after_optimize_objective"] - result["before_optimize_objective"]).abs() \
            / result["before_optimize_objective"]

        return result
