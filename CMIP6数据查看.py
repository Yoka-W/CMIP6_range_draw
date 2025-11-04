# 导入必要的库
import xarray as xr

# 设置 CMIP6 .nc 文件路径（替换为你的实际路径）
file_path = r"G:\2-Data\5-CMIP6\ssp126\rsds_3hr_ACCESS-CM2_ssp126_r1i1p1f1_gn_2015-2100_china.nc"  # 例如：'G:\\2-Data\\5-CMIP6\\ssp126_diff\\rsdsdiff_3hr_ACCESS-CM2_ssp126_r1i1p1f1_gn_2015-2100_china.nc'


# 函数：读取并打印 CMIP6 .nc 文件的元数据信息
def read_cmip6_metadata(file_path):
    """
    读取 CMIP6 .nc 文件的元数据信息，包括维度、变量、全局属性和变量属性。
    - file_path: .nc 文件路径
    """
    try:
        # 打开数据集
        ds = xr.open_dataset(file_path, decode_times=True, use_cftime=True)  # 使用 cftime 处理 CMIP6 时间格式

        # 打印整体数据集信息
        print("数据集整体信息:")
        print(ds)
        print("\n")

        # 打印维度
        print("维度 (Dimensions):")
        print(ds.dims)
        print("\n")

        # 打印变量列表
        print("变量 (Variables):")
        print(ds.variables)
        print("\n")

        # 打印全局属性
        print("全局属性 (Global Attributes):")
        for key, value in ds.attrs.items():
            print(f"{key}: {value}")
        print("\n")

        # 打印每个变量的属性（可选：针对特定变量，如 'rsds' 或所有变量）
        print("变量属性 (Variable Attributes):")
        for var_name in ds.variables:
            print(f"变量 '{var_name}':")
            for attr_key, attr_value in ds[var_name].attrs.items():
                print(f"  {attr_key}: {attr_value}")
            print("\n")

        # 关闭数据集
        ds.close()
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")


# 主程序：读取元数据
if __name__ == "__main__":
    print(f"读取文件: {file_path}")
    read_cmip6_metadata(file_path)