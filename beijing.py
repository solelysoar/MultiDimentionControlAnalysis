import os
import pandas as pd
from ControlAnalysis import ControlAnalysis

data_path = 'data/lx_data.csv'
if not os.path.exists(data_path):
    print("test data not ready")
else:
    df_test = pd.read_csv(data_path)
    tool = ControlAnalysis()
    result = tool.control_direction_explore(df_test,
                                            condition_columns=["OutsideDryBulb", "OutsideWebBulb",
                                                               "ch(lx)_current_percent"],
                                            condition_tolerance=[1, 1, 2],
                                            control_columns=["actual_scw_water_temperature_diff",
                                                             "scw_close_to_wet_bulb_temperature",
                                                             "actual_sch_water_temperature_diff"],
                                            objective_column="system_total_power",
                                            ascending=False,
                                            min_points=3)  # traversal total time 8 min 56 seconds
    result.to_csv("total_power_lx.csv")

