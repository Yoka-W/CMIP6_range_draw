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

# NC文件路径（四个模式的CMIP6未来数据文件，选择较高分辨率模式）
nc_path1 = r'G:\2-Data\5-CMIP6\ssp245\rsds_3hr_BCC-CSM2-MR_ssp245_r1i1p1f1_gn_2015-2100_china.nc'  # 第一模式（BCC-CSM2-MR）
nc_path2 = r'G:\2-Data\5-CMIP6\ssp245\rsds_3hr_CMCC-CM2-SR5_ssp245_r1i1p1f1_gn_2015-2100_china.nc'  # 第二模式（CMCC-CM2-SR5，替换为实际路径）
nc_path3 = r'G:\2-Data\5-CMIP6\ssp245\rsds_3hr_CMCC-ESM2_ssp245_r1i1p1f1_gn_2015-2100_china.nc'  # 第三模式（CMCC-ESM2，替换为实际路径）
nc_path4 = r'G:\2-Data\5-CMIP6\ssp245\rsds_3hr_MRI-ESM2-0_ssp245_r1i1p1f1_gn_2015-2100_china.nc'  # 第四模式（MRI-ESM2-0，替换为实际路径）

# 多个矢量文件路径列表（Shapefiles）
shp_paths = [
    r'C:\Users\汪永康\Desktop\调研制图\榆林市.shp',
    r'C:\Users\汪永康\Desktop\调研制图\鄂尔多斯市.shp',
    r'C:\Users\汪永康\Desktop\调研制图\渑池县.shp',
    r'C:\Users\汪永康\Desktop\调研制图\西安市.shp',
    # 添加更多矢量文件路径，如果有
]

# 读取四个NC文件（使用chunks处理大文件）
ds1 = xr.open_dataset(nc_path1, chunks={'time': 1000})
da1 = ds1['rsds']  # 变量名

ds2 = xr.open_dataset(nc_path2, chunks={'time': 1000})
da2 = ds2['rsds']  # 变量名

ds3 = xr.open_dataset(nc_path3, chunks={'time': 1000})
da3 = ds3['rsds']  # 变量名

ds4 = xr.open_dataset(nc_path4, chunks={'time': 1000})
da4 = ds4['rsds']  # 变量名

# 设置CRS（假设为WGS84，经纬度坐标）
for da in [da1, da2, da3, da4]:
    da.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
    da.rio.write_crs('EPSG:4326', inplace=True)

# 选择2025-2100时间范围，并计算年均值（因为数据是3hr，先resample到年均，使用'YE'避免警告）
da_future1 = da1.sel(time=slice('2025', '2100'))
annual_da1 = da_future1.resample(time='YE').mean(dim='time')  # 年均值

da_future2 = da2.sel(time=slice('2025', '2100'))
annual_da2 = da_future2.resample(time='YE').mean(dim='time')  # 年均值

da_future3 = da3.sel(time=slice('2025', '2100'))
annual_da3 = da_future3.resample(time='YE').mean(dim='time')  # 年均值

da_future4 = da4.sel(time=slice('2025', '2100'))
annual_da4 = da_future4.resample(time='YE').mean(dim='time')  # 年均值

# 获取所有模式的年份集合，并找到共同年份
years1 = annual_da1.time.dt.year.values
years2 = annual_da2.time.dt.year.values
years3 = annual_da3.time.dt.year.values
years4 = annual_da4.time.dt.year.values

all_years = sorted(set(years1) | set(years2) | set(years3) | set(years4))

# 时间序列（基于所有可能年份）
years = np.array(all_years)

# 对于每个矢量文件处理
for shp_path in shp_paths:
    # 读取矢量文件
    gdf = gpd.read_file(shp_path)
    # 假设CRS为WGS84，如果不同请转换：gdf = gdf.to_crs('EPSG:4326')

    # 剪裁到矢量区域（使用clip）
    clipped_da1 = annual_da1.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)
    clipped_da2 = annual_da2.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)
    clipped_da3 = annual_da3.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)
    clipped_da4 = annual_da4.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)

    # 计算每个年的区域均值（忽略NaN，单位W/m²；如果需转换为W/km²，添加 means *= 1e6）
    means1 = clipped_da1.mean(dim=['lat', 'lon'], skipna=True).values
    means2 = clipped_da2.mean(dim=['lat', 'lon'], skipna=True).values
    means3 = clipped_da3.mean(dim=['lat', 'lon'], skipna=True).values
    means4 = clipped_da4.mean(dim=['lat', 'lon'], skipna=True).values

    # 创建完整数组，填充NaN
    full_means1 = np.full(len(years), np.nan)
    full_means2 = np.full(len(years), np.nan)
    full_means3 = np.full(len(years), np.nan)
    full_means4 = np.full(len(years), np.nan)

    # 填充有效数据
    idx1 = np.isin(years, years1)
    full_means1[idx1] = means1[:len(idx1[idx1 == True])]  # 截断以匹配长度

    idx2 = np.isin(years, years2)
    full_means2[idx2] = means2[:len(idx2[idx2 == True])]

    idx3 = np.isin(years, years3)
    full_means3[idx3] = means3[:len(idx3[idx3 == True])]

    idx4 = np.isin(years, years4)
    full_means4[idx4] = means4[:len(idx4[idx4 == True])]

    # 求四种模式的均值，忽略NaN
    means_stack = np.stack([full_means1, full_means2, full_means3, full_means4], axis=0)
    means_avg = np.nanmean(means_stack, axis=0)

    # 获取矢量文件名（不含路径和扩展名）
    base_name = os.path.basename(shp_path).replace('.shp', '')

    # 绘制折线图（变化序列，假设是年均值趋势作为变化图）
    plt.figure(figsize=(10, 6))
    plt.plot(years, means_avg, marker='o', linestyle='-', color='b')
    plt.title(f'中等排放情景下{base_name}未来辐射年均值变化（四种模式平均）', fontproperties=prop,fontsize=14)
    plt.xlabel('年份', fontproperties=prop,fontsize=14)
    plt.ylabel('瓦特每平方米', fontproperties=prop,fontsize=14)  # 假设是m²；如果真是km²，修改为'瓦特每平方千米'并 *=1e6
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