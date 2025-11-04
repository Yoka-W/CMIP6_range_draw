import xarray as xr
import geopandas as gpd
import rioxarray
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import mapping
import matplotlib.font_manager as fm
import os  # 新增导入os模块以正确处理路径

# 设置支持中文的字体路径（宋体，Windows常用SimSun）
# 如果没有字体，可以下载字体文件并指定路径
font_path = 'C:/Windows/Fonts/simsun.ttc'  # Windows示例，替换为实际路径（宋体通常为simsun.ttc）
prop = fm.FontProperties(fname=font_path)

# NC文件路径
nc_path = r'G:\2-Data\1-Radiation\3-CMFD\srad_CMFD_V0200_B-01_01yr_010deg_1951-2024.nc'

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
var_name = 'srad'
da = ds[var_name]

# 设置CRS（假设为WGS84，经纬度坐标）
da.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
da.rio.write_crs('EPSG:4326', inplace=True)

# 时间序列（假设时间从1951到2024）
years = np.arange(1951, 2025)  # 调整如果时间不同

# 对于每个矢量文件处理
for shp_path in shp_paths:
    # 读取矢量文件
    gdf = gpd.read_file(shp_path)
    # 假设CRS为WGS84，如果不同请转换：gdf = gdf.to_crs('EPSG:4326')

    # 剪裁到矢量区域（使用clip）
    clipped_da = da.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)

    # 计算每个时间步的均值（忽略NaN）
    means = clipped_da.mean(dim=['lat', 'lon'], skipna=True).values

    # 获取矢量文件名（不含路径和扩展名）
    base_name = os.path.basename(shp_path).replace('.shp', '')

    # 绘制折线图
    plt.figure(figsize=(10, 6))
    plt.plot(years, means, marker='o', linestyle='-', color='g')
    plt.title(f'{base_name}区域辐射年均值', fontproperties=prop,fontsize=14)
    plt.xlabel('年份', fontproperties=prop,fontsize=14)
    plt.ylabel('瓦特每平方米', fontproperties=prop,fontsize=14)
    y_min = 130
    y_max = 210
    plt.ylim(y_min, y_max)
    plt.grid(True)
    plt.tight_layout()

    # 保存或显示图（这里保存为PNG，用户可选择plt.show()）
    output_path = f'{base_name}_hist_line_chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()  # 关闭图以释放内存

print("处理完成，所有折线图已生成。")