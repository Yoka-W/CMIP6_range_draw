import xarray as xr
import rioxarray
from affine import Affine


def calculate_band_mean(input_path, output_path, start_band, end_band):
    """
    计算指定波段范围内的栅格均值并导出为GeoTIFF

    参数:
        input_path: 输入NetCDF文件路径
        output_path: 输出TIFF文件路径
        start_band: 起始波段索引(从1开始)
        end_band: 结束波段索引(包含)
    """
    # 打开NetCDF文件
    ds = xr.open_dataset(input_path)

    # 检查波段范围是否有效
    total_bands = len(ds['time'])
    if start_band < 1 or end_band > total_bands or start_band > end_band:
        raise ValueError(f"波段范围无效，文件共有{total_bands}个波段")

    # 选择指定波段范围的数据(注意Python是0-based索引)
    srad_selected = ds['srad'].isel(time=slice(start_band - 1, end_band))

    # 计算时间维度上的均值，跳过缺失值
    mean_srad = srad_selected.mean(dim='time', skipna=True)

    # 设置地理信息
    mean_srad.rio.write_crs("EPSG:4326", inplace=True)  # WGS84坐标系

    # 创建Affine变换对象
    transform = Affine(
        (139.9999969438762832 - 70.0000030561237025) / 700, 0, 70.0000030561237025,
        0, (15.0000001900178148 - 55.0000007636565016) / 400, 55.0000007636565016
    )
    mean_srad.rio.write_transform(transform, inplace=True)
    mean_srad.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)

    # 设置缺失值并导出
    mean_srad.rio.write_nodata(1e+20, inplace=True)
    mean_srad.rio.to_raster(output_path, dtype='float32')

    print(f"成功计算波段{start_band}-{end_band}的均值，结果已保存到: {output_path}")
    print(f"对应年份: {start_band + 1950}-{end_band + 1950}")


# 使用示例
if __name__ == "__main__":
    input_nc = "G:/2-Data/1-Radiation/3-CMFD/srad_CMFD_V0200_B-01_01yr_010deg_1951-2024.nc"
    output_tif = "G:/2-Data/1-Radiation/3-CMFD/srad_band_mean_2005-2024.tif"

    # 在这里设置您想要的波段范围(1-74)
    start_band = 55  # 1951年(第1个波段)
    end_band = 74  # 1960年(第10个波段)

    calculate_band_mean(input_nc, output_tif, start_band, end_band)