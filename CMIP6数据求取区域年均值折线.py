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

# NC文件路径（你的CMIP6未来数据文件）
nc_path = r'G:\2-Data\5-CMIP6\ssp245\rsds_3hr_BCC-CSM2-MR_ssp245_r1i1p1f1_gn_2015-2100_china.nc'  # 替换为实际路径，如果是SSP2-4.5或其他情景，调整路径

# 多个矢量文件路径列表（Shapefiles）
shp_paths = [
    r'C:\Users\汪永康\Desktop\调研制图\榆林市.shp',
    r'C:\Users\汪永康\Desktop\调研制图\鄂尔多斯市.shp',
    r'C:\Users\汪永康\Desktop\调研制图\渑池县.shp',
    r'C:\Users\汪永康\Desktop\调研制图\西安市.shp',
    # 添加更多矢量文件路径，如果有
]

# 读取NC文件（使用chunks处理大文件）
ds = xr.open_dataset(nc_path, chunks={'time': 1000})
var_name = 'rsds'  # 变量名
da = ds[var_name]

# 设置CRS（假设为WGS84，经纬度坐标）
da.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
da.rio.write_crs('EPSG:4326', inplace=True)

# 选择2025-2100时间范围，并计算年均值（因为数据是3hr，先resample到年均）
da_future = da.sel(time=slice('2025', '2100'))
annual_da = da_future.resample(time='Y').mean(dim='time')  # 年均值

# 时间序列（2025到2100）
years = np.arange(2025, 2101)

# 对于每个矢量文件处理
for shp_path in shp_paths:
    # 读取矢量文件
    gdf = gpd.read_file(shp_path)
    # 假设CRS为WGS84，如果不同请转换：gdf = gdf.to_crs('EPSG:4326')

    # 剪裁到矢量区域（使用clip）
    clipped_da = annual_da.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)

    # 计算每个年的区域均值（忽略NaN，单位W/m²；如果需转换为W/km²，添加 means *= 1e6）
    means = clipped_da.mean(dim=['lat', 'lon'], skipna=True).values

    # 获取矢量文件名（不含路径和扩展名）
    base_name = os.path.basename(shp_path).replace('.shp', '')

    # 绘制折线图（变化序列，假设是年均值趋势作为变化图）
    plt.figure(figsize=(10, 6))
    plt.plot(years, means, marker='o', linestyle='-', color='g')
    plt.title(f'中等排放情景下{base_name} 未来辐射年均值变化（BCC-CSM2-MR）', fontproperties=prop)
    plt.xlabel('年份', fontproperties=prop)
    plt.ylabel('瓦特每平方米', fontproperties=prop)  # 假设是m²；如果真是km²，修改为'瓦特每平方千米'并 *=1e6
    y_min = 130  # 可调整
    y_max = 210  # 可调整
    plt.ylim(y_min, y_max)
    plt.grid(True)
    plt.tight_layout()

    # 保存或显示图（这里保存为PNG，用户可选择plt.show()）
    output_path = f'{base_name}_future_line_chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()  # 关闭图以释放内存

print("处理完成，所有折线图已生成。")