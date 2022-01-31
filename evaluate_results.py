from os import listdir
from os.path import isfile, join
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook


def main():
    # %%
    from os import listdir
    from os.path import isfile, join
    from pathlib import Path

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    variant_approach_results_path = Path(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results\results_VARIANTS\noImprInLoop_adaptive_OD')

    listdir(variant_approach_results_path)

    xixi_cc_results_path_no_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results_xixi\noImprInLoop_default_OD\exp_xixi_cc_100')
    xixi_cd_results_path_no_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results_xixi\noImprInLoop_default_OD\exp_xixi_cd_100')

    xixi_cc_results_path_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results_xixi\imprInLoop_adaptive_OD\exp_xixi_cc_100')
    xixi_cd_results_path_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results_xixi\imprInLoop_adaptive_OD\exp_xixi_cd_100')

    file_paths_variant_approach = [join(variant_approach_results_path, f) for f in
                                   listdir(variant_approach_results_path) if
                                   isfile(join(variant_approach_results_path, f))]
    file_paths_xixi_cc_no_impr_loop = [join(xixi_cc_results_path_no_impr_loop, f) for f in
                                       listdir(xixi_cc_results_path_no_impr_loop) if
                                       isfile(join(xixi_cc_results_path_no_impr_loop, f))]
    file_paths_xixi_cd_no_impr_loop = [join(xixi_cd_results_path_no_impr_loop, f) for f in
                                       listdir(xixi_cd_results_path_no_impr_loop) if
                                       isfile(join(xixi_cd_results_path_no_impr_loop, f))]

    file_paths_xixi_cc_impr_loop = [join(xixi_cc_results_path_impr_loop, f) for f in
                                    listdir(xixi_cc_results_path_impr_loop) if
                                    isfile(join(xixi_cc_results_path_impr_loop, f))]
    file_paths_xixi_cd_impr_loop = [join(xixi_cd_results_path_impr_loop, f) for f in
                                    listdir(xixi_cd_results_path_impr_loop) if
                                    isfile(join(xixi_cd_results_path_impr_loop, f))]

    file_paths_xixi_cc = file_paths_xixi_cc_impr_loop + file_paths_xixi_cc_no_impr_loop
    file_paths_xixi_cd = file_paths_xixi_cd_impr_loop + file_paths_xixi_cd_no_impr_loop

    def get_results(df):
        return df['ARI'].mean(), df['Precision Align'].mean(), df.groupby(['Name'])['Precision Align'].max().mean(), \
               df.groupby(['Name'])['ARI'].max().mean(), df['Xixi Precision'].mean(), df.groupby(['Name'])['Xixi Precision'].max().mean()

    def get_results_xixi(df):
        return df['Refined Log ARI'].mean(), df['Refined Log Precision'].mean(), df.groupby(['Name'])[
            'Refined Log Precision'].max().mean(), df.groupby(['Name'])['Refined Log ARI'].max().mean()

    # %%

    dfs = []
    for path in file_paths_variant_approach:
        if 'png' in path:
            continue
        temp = pd.read_csv(path)
        for i in range(166, len(temp), 330):
            end = min(len(temp), i + 165)
            temp.loc[i:end, 'use_frequency'] = True
        dfs.append(temp)

    df = pd.DataFrame(np.concatenate([df_temp.values for df_temp in dfs]), columns=dfs[0].columns)

    # df = df.loc[df['use_frequency'] == True]
    # df = df.loc[df['window_size'] == 4]
    # df = df.loc[df['distance_metric'] == 'DistanceVariant.MULTISET_DISTANCE']
    # df = df.loc[df['threshold'] < 0.8]

    ari, prec, average_max_prec, average_max_ari, xixi_prec, average_xixi_max_prec = get_results(df)
    print('My approach')
    print('ARI')
    print(ari)
    print(average_max_ari)
    print('Precision')
    print(prec)
    print(average_max_prec)
    print('Xixi Precision')
    print(xixi_prec)
    print(average_xixi_max_prec)

    # %%

    plt.figure()
    bp = df.boxplot(by=['threshold'], column=['ARI'], grid=False)
    plt.show()

    plt.figure()
    bp = df.boxplot(by=['window_size'], column=['ARI'], grid=False)
    plt.show()

    # plt.figure()
    # bp = df.boxplot(by=['use_combined_context'], column=['ARI'], grid=False)
    # plt.show()

    plt.figure()
    bp = df.boxplot(by=['use_frequency'], column=['ARI'], grid=False)
    plt.show()

    plt.figure()
    bp = df.boxplot(by=['distance_metric'], column=['ARI'], grid=False)
    plt.show()
    # %%

    plt.figure()
    bp = df.boxplot(by=['use_frequency', 'distance_metric', 'window_size'], column=['Precision Align'], grid=False,
                    figsize=(100, 10), fontsize='small')
    plt.savefig(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results\results_VARIANTS\imprInLoop_adaptive_OD\precision.png')

    plt.figure()
    bp = df.boxplot(by=['use_frequency', 'distance_metric', 'window_size'], column=['ARI'], grid=False,
                    figsize=(100, 10), fontsize='small')
    plt.savefig(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results\results_VARIANTS\imprInLoop_adaptive_OD\ari.png')

    # %%
    dfs_xixi_cc = []
    for path in file_paths_xixi_cc:
        dfs_xixi_cc.append(pd.read_csv(path))

    df_xixi_cc = pd.DataFrame(np.concatenate([df_temp.values for df_temp in dfs_xixi_cc]),
                              columns=dfs_xixi_cc[0].columns)

    df_xixi_cc['Name'] = df_xixi_cc['Folder'] + '/' + df_xixi_cc['Log']
    print('Base Data:')
    print(df_xixi_cc['Original Model Precision'].mean())
    print(df_xixi_cc['Precise Log Precision '].mean())
    print(df_xixi_cc['Unrefined Log Precision'].mean())
    print(df_xixi_cc['Xixi Log Precision'].mean())

    # df_xixi_cc = df_xixi_cc.loc[df_xixi_cc['Unfolding Threshold'] > 0.5]

    ari, prec, average_max_prec, average_max_ari = get_results_xixi(df_xixi_cc)

    print('Xixi CC')
    print('ARI')
    print(ari)
    print(average_max_ari)
    print('Precision')
    print(prec)
    print(average_max_prec)

    # %%
    plt.figure()
    bp = df_xixi_cc.boxplot(column=['Refined Log Precision'], grid=False, )
    plt.show()

    plt.figure()
    bp = df_xixi_cc.boxplot(column=['Refined Log ARI'], grid=False)
    plt.show()

    plt.figure()
    bp = df_xixi_cc.boxplot(by='Unfolding Threshold', column=['Refined Log Precision'], grid=False, )
    plt.show()

    plt.figure()
    bp = df_xixi_cc.boxplot(by='Unfolding Threshold', column=['Refined Log ARI'], grid=False)
    plt.show()

    # %%

    dfs_xixi_cd = []
    for path in file_paths_xixi_cd:
        dfs_xixi_cd.append(pd.read_csv(path))
    df_xixi_cd = pd.DataFrame(np.concatenate([df_temp.values for df_temp in dfs_xixi_cd]),
                              columns=dfs_xixi_cd[0].columns)

    df_xixi_cd['Name'] = df_xixi_cd['Folder'] + '/' + df_xixi_cd['Log']

    # df_xixi_cd = df_xixi_cd.loc[df_xixi_cd['Unfolding Threshold'] > 0.5]

    ari, prec, average_max_prec, average_max_ari = get_results_xixi(df_xixi_cd)
    print('Xixi CD')
    print('ARI')
    print(ari)
    print(average_max_ari)
    print('Precision')
    print(prec)
    print(average_max_prec)

    # %%

    plt.figure()
    bp = df_xixi_cd.boxplot(column=['Refined Log Precision'], grid=False)
    plt.show()

    plt.figure()
    bp = df_xixi_cd.boxplot(column=['Refined Log ARI'], grid=False)
    plt.show()

    plt.figure()
    bp = df_xixi_cd.boxplot(by='Variant Threshold', column=['Refined Log Precision'], grid=False, )
    plt.show()

    plt.figure()
    bp = df_xixi_cd.boxplot(by='Variant Threshold', column=['Refined Log ARI'], grid=False)
    plt.show()


main()
