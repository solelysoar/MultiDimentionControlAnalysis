import pandas as pd
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

df_721 = pd.read_csv("data/机房721.csv")
df_721.index = pd.to_datetime(df_721["Time"])

room_length = 21
room_width = 10
grid_width = 1

x = np.arange(0, room_length, grid_width)
y = np.arange(0, room_width, grid_width)
X, Y = np.meshgrid(x, y)

# setup columns to plot
# rule for "column_name": in case that two columns have similar name, e.g. user wants to plot "Temperature" rather than
# "Setting Temperature". A simple string rule was introduced. For condition as aforementioned, user could use
# "{desired name}~{exclude name}" to do filtering. e.g. "Temperature~Setting Temperature".
# Warning: (1) does not support original name with "~"; (2) does not support more than one exclusion
plot_info = {
    "column_name": "送风温度~送风温度设定值",
    "plot_title": "Return Set Temp",
    "save_gif": 0,
    "save_gif_path": "721_20190802_20190804_Rset.gif"
}

start_time = "2019-08-02 00:00"
end_time = "2019-08-04 00:00"
if "~" in plot_info["column_name"]:
    incol = plot_info["column_name"].split("~")[0]
    outcol = plot_info["column_name"].split("~")[1]
    Rtemp_columns = [_name for _name in df_721.columns if (incol in _name) and (outcol not in _name)]
else:
    incol = plot_info["column_name"]
    Rtemp_columns = [_name for _name in df_721.columns if (plot_info["column_name"] in _name)]
_tmp = df_721.loc[start_time:end_time, Rtemp_columns]

# has to manually change location of room ac
ac_location = {
    "_1": [0, [0, 4]],
    "_2": [0, [9, 12]],
    "_3": [0, [17, 21]],
    "_5": [len(y)-1, [0, 4]],
    "_6": [len(y)-1, [9, 12]],
    "_7": [len(y)-1, [17, 21]]
              }


def update(index):
    ax.clear()
    row = _tmp.iloc[index]
    # simulate temperature distribution
    temp_grid = pd.DataFrame(np.full((len(y), len(x)), np.nan))  # initialization
    for key, value in ac_location.items():
        column_name = f"721.{key}#{incol}"
        write_value = row[column_name]

        write_x = value[0]
        write_y_left = value[1][0]
        write_y_right = value[1][1]
        temp_grid.iloc[write_x, write_y_left:write_y_right] = write_value
    temp_grid = temp_grid.interpolate(axis=0).interpolate(axis=1)
    Z = temp_grid.values

    ax.set_title(f"Room 721 {plot_info['plot_title']} Distribution {row.name}")
    ax.contourf(X, Y, Z, **kw)


fig, ax = plt.subplots(figsize=(10, 5))
# generate colorbar based on used data
# zmin = _tmp.min().min()
# zmax = _tmp.max().max()
# generate color based on fixed data
zmin = 15
zmax = 28
levels = np.linspace(zmin, zmax, 100)

kw = dict(levels=levels, cmap=plt.cm.jet, vmin=zmin, vmax=zmax, origin='lower')
# set up first image
row = _tmp.iloc[0]
# 计算温度场
temp_grid = pd.DataFrame(np.full((len(y), len(x)), np.nan))  # initialization
for key, value in ac_location.items():
    column_name = f"721.{key}#{incol}"
    write_value = row[column_name]

    write_x = value[0]
    write_y_left = value[1][0]
    write_y_right = value[1][1]
    temp_grid.iloc[write_x, write_y_left:write_y_right] = write_value
temp_grid = temp_grid.interpolate(axis=0).interpolate(axis=1)
Z = temp_grid.values

ax.set_title(f"Room 721 {plot_info['plot_title']} Distribution {row.name}")
fill = ax.contourf(X, Y, Z, **kw)
cbar = plt.colorbar(fill)

ani = animation.FuncAnimation(fig, update, frames=np.arange(1, len(_tmp)), interval=100, blit=False)
if plot_info["save_gif"]:
    ani.save(plot_info["save_gif_path"], writer='pillow')  # 保存gif
else:
    plt.show() # 实时显示