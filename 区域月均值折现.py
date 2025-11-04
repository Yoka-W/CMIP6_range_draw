import xarray as xr
import geopandas as gpd
import rioxarray
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import mapping
import matplotlib.font_manager as fm
import os  # 新增导入os模块以正确处理路径
from matplotlib.dates import DateFormatter  # 新增导入以格式化日期轴

# 设置支持中文的字体路径（宋体，Windows常用SimSun）
# 如果没有字体，可以下载字体文件并指定路径
font_path = 'C:/Windows/Fonts/simsun.ttc'  # Windows示例，替换为实际路径（宋体通常为simsun.ttc）
prop = fm.FontProperties(fname=font_path)

# NC文件路径（假设现在是逐月数据文件，路径需调整为实际逐月NC文件）
nc_path = r"G:\2-Data\1-Radiation\3-CMFD\srad_CMFD_V0200_B-01_01mo_010deg_195101-202412.nc"  # 示例路径，替换为实际逐月文件路径

# 多个矢量文件路径列表（Shapefiles），用户需替换为实际路径
shp_paths = [
    r'C:\Users\汪永康\Desktop\调研制图\榆林市.shp',
    r'C:\Users\汪永康\Desktop\调研制图\鄂尔多斯市.shp',
    r'C:\Users\汪永康\Desktop\调研制图\渑池县.shp',
    r'C:\Users\汪永康\Desktop\调研制图\西安市.shp',
    # 添加更多矢量文件路径，如果有
]

# 读取NC文件
ds = xr.open_dataset(nc_path)
# 假设变量名为'srad'，时间维度名为'time'，经纬度为'lon'和'lat'
# 如果实际变量名不同，请调整
var_name = 'srad'  # 假设变量名
da = ds[var_name]

# 设置CRS（假设为WGS84，经纬度坐标）
da.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
da.rio.write_crs('EPSG:4326', inplace=True)

# 对于每个矢量文件处理
for shp_path in shp_paths:
    # 读取矢量文件
    gdf = gpd.read_file(shp_path)
    # 假设CRS为WGS84，如果不同请转换：gdf = gdf.to_crs('EPSG:4326')

    # 剪裁到矢量区域（使用clip）
    clipped_da = da.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)

    # 计算每个月份的区域均值（忽略NaN）
    means = clipped_da.mean(dim=['lat', 'lon'], skipna=True).values

    # 时间序列（假设'time'维度为datetime格式，如果不是，可添加 da['time'] = pd.to_datetime(da['time'])）
    times = clipped_da.time.values

    # 获取矢量文件名（不含路径和扩展名）
    base_name = os.path.basename(shp_path).replace('.shp', '')

    # 绘制折线图（由于数据点多，调整figsize以显示长序列）
    plt.figure(figsize=(20, 6))  # 增加宽度以适应长序列
    plt.plot(times, means, marker='o', linestyle='-', color='r', markersize=2)  # 减小marker大小以避免拥挤
    plt.title(f'{base_name} 区域辐射逐月值 (1951-01 到 2024-12)', fontproperties=prop)
    plt.xlabel('时间', fontproperties=prop)
    plt.ylabel('辐射均值 (单位取决于数据)', fontproperties=prop)

    # 格式化x轴为年-月
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()  # 旋转日期标签以避免重叠

    plt.grid(True)
    plt.tight_layout()

    # 保存或显示图（这里保存为PNG，用户可选择plt.show()）
    output_path = f'{base_name}_monthly_series_line_chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()  # 关闭图以释放内存

print("处理完成，所有折线图已生成。")