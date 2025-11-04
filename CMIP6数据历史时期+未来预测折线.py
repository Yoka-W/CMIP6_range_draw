import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to avoid Tkinter issues
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

# 历史数据路径（三个模式：BCC-CSM2-MR, CMCC-CM2-SR5, CMCC-ESM2；基于截图更新路径为\hist\）
hist_path1 = r'G:\2-Data\5-CMIP6\hist\rsds_3hr_BCC-CSM2-MR_historical_r1i1p1f1_gn_1980-2014_china.nc'  # BCC-CSM2-MR
hist_path2 = r'G:\2-Data\5-CMIP6\hist\rsds_3hr_CMCC-CM2-SR5_historical_r1i1p1f1_gn_1980-2014_china.nc'  # CMCC-CM2-SR5
hist_path3 = r'G:\2-Data\5-CMIP6\hist\rsds_3hr_CMCC-ESM2_historical_r1i1p1f1_gn_1980-2014_china.nc'  # CMCC-ESM2

# 未来数据路径（四个模式，包括MRI-ESM2-0）
fut_path1 = r'G:\2-Data\5-CMIP6\ssp245\rsds_3hr_BCC-CSM2-MR_ssp245_r1i1p1f1_gn_2015-2100_china.nc'  # BCC-CSM2-MR
fut_path2 = r'G:\2-Data\5-CMIP6\ssp245\rsds_3hr_CMCC-CM2-SR5_ssp245_r1i1p1f1_gn_2015-2100_china.nc'  # CMCC-CM2-SR5
fut_path3 = r'G:\2-Data\5-CMIP6\ssp245\rsds_3hr_CMCC-ESM2_ssp245_r1i1p1f1_gn_2015-2100_china.nc'  # CMCC-ESM2
fut_path4 = r'G:\2-Data\5-CMIP6\ssp245\rsds_3hr_MRI-ESM2-0_ssp245_r1i1p1f1_gn_2015-2100_china.nc'  # MRI-ESM2-0

# 多个矢量文件路径列表（Shapefiles）
shp_paths = [
    r'C:\Users\汪永康\Desktop\调研制图\榆林市.shp',
    r'C:\Users\汪永康\Desktop\调研制图\鄂尔多斯市.shp',
    r'C:\Users\汪永康\Desktop\调研制图\渑池县.shp',
    r'C:\Users\汪永康\Desktop\调研制图\西安市.shp',
    # 添加更多矢量文件路径，如果有
]

# 读取历史NC文件（使用chunks处理大文件）
ds_hist1 = xr.open_dataset(hist_path1, chunks={'time': 1000})
da_hist1 = ds_hist1['rsds']  # 变量名

ds_hist2 = xr.open_dataset(hist_path2, chunks={'time': 1000})
da_hist2 = ds_hist2['rsds']  # 变量名

ds_hist3 = xr.open_dataset(hist_path3, chunks={'time': 1000})
da_hist3 = ds_hist3['rsds']  # 变量名

# 读取未来NC文件
ds_fut1 = xr.open_dataset(fut_path1, chunks={'time': 1000})
da_fut1 = ds_fut1['rsds']  # 变量名

ds_fut2 = xr.open_dataset(fut_path2, chunks={'time': 1000})
da_fut2 = ds_fut2['rsds']  # 变量名

ds_fut3 = xr.open_dataset(fut_path3, chunks={'time': 1000})
da_fut3 = ds_fut3['rsds']  # 变量名

ds_fut4 = xr.open_dataset(fut_path4, chunks={'time': 1000})
da_fut4 = ds_fut4['rsds']  # 变量名

# 设置CRS（假设为WGS84，经纬度坐标）
for da in [da_hist1, da_hist2, da_hist3, da_fut1, da_fut2, da_fut3, da_fut4]:
    da.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
    da.rio.write_crs('EPSG:4326', inplace=True)

# 计算历史年均值（1980-2014，使用'YE'避免警告）
annual_hist1 = da_hist1.resample(time='YE').mean(dim='time')
annual_hist2 = da_hist2.resample(time='YE').mean(dim='time')
annual_hist3 = da_hist3.resample(time='YE').mean(dim='time')

# 计算未来年均值（2015-2100）
annual_fut1 = da_fut1.resample(time='YE').mean(dim='time')
annual_fut2 = da_fut2.resample(time='YE').mean(dim='time')
annual_fut3 = da_fut3.resample(time='YE').mean(dim='time')
annual_fut4 = da_fut4.resample(time='YE').mean(dim='time')

# 获取所有年份（历史 + 未来）
hist_years = annual_hist1.time.dt.year.values  # 假设所有历史模式年份相同
fut_years = annual_fut1.time.dt.year.values  # 假设所有未来模式年份相同
all_years = np.concatenate((hist_years, fut_years))

# 对于每个矢量文件处理
for shp_path in shp_paths:
    # 读取矢量文件
    gdf = gpd.read_file(shp_path)
    # 假设CRS为WGS84，如果不同请转换：gdf = gdf.to_crs('EPSG:4326')

    # 剪裁历史数据到矢量区域
    clipped_hist1 = annual_hist1.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)
    clipped_hist2 = annual_hist2.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)
    clipped_hist3 = annual_hist3.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)

    # 剪裁未来数据到矢量区域
    clipped_fut1 = annual_fut1.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)
    clipped_fut2 = annual_fut2.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)
    clipped_fut3 = annual_fut3.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)
    clipped_fut4 = annual_fut4.rio.clip(gdf.geometry.apply(mapping), gdf.crs, drop=True, all_touched=True)

    # 计算历史每个年的区域均值（忽略NaN，单位W/m²）
    means_hist1 = clipped_hist1.mean(dim=['lat', 'lon'], skipna=True).values
    means_hist2 = clipped_hist2.mean(dim=['lat', 'lon'], skipna=True).values
    means_hist3 = clipped_hist3.mean(dim=['lat', 'lon'], skipna=True).values

    # 计算未来每个年的区域均值
    means_fut1 = clipped_fut1.mean(dim=['lat', 'lon'], skipna=True).values
    means_fut2 = clipped_fut2.mean(dim=['lat', 'lon'], skipna=True).values
    means_fut3 = clipped_fut3.mean(dim=['lat', 'lon'], skipna=True).values
    means_fut4 = clipped_fut4.mean(dim=['lat', 'lon'], skipna=True).values

    # 历史时期平均（3个模式）
    means_hist_avg = np.nanmean(np.stack([means_hist1, means_hist2, means_hist3], axis=0), axis=0)

    # 未来时期平均（4个模式）
    means_fut_avg = np.nanmean(np.stack([means_fut1, means_fut2, means_fut3, means_fut4], axis=0), axis=0)

    # 合并历史和未来平均值
    means_avg = np.concatenate((means_hist_avg, means_fut_avg))

    # 获取矢量文件名（不含路径和扩展名）
    base_name = os.path.basename(shp_path).replace('.shp', '')

    # 绘制折线图
    plt.figure(figsize=(10, 6))
    plt.plot(all_years, means_avg, marker='o', linestyle='-', color='b')
    plt.title(f'中等排放情景下{base_name}辐射年均值变化（1980-2100，模式集合平均）', fontproperties=prop, fontsize=14)
    plt.xlabel('年份', fontproperties=prop, fontsize=14)
    plt.ylabel('瓦特每平方米', fontproperties=prop, fontsize=14)  # 假设是m²；如果真是km²，修改为'瓦特每平方千米'并 *=1e6
    y_min = 130  # 可调整
    y_max = 210  # 可调整
    plt.ylim(y_min, y_max)
    plt.grid(True)
    plt.tight_layout()

    # 保存或显示图（这里保存为PNG，用户可选择plt.show()）
    output_path = f'{base_name}_1980_2100_line_chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()  # 关闭图以释放内存

print("处理完成，所有折线图已生成。")