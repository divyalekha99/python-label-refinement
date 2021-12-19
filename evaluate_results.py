from os import listdir
from os.path import isfile, join
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook


def main():
    #%%
    from os import listdir
    from os.path import isfile, join
    from pathlib import Path

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.cbook as cbook

    event_approach_results_path = Path(r'C:\Users\Jonas\Desktop\pm-label-splitting\results\results')

    listdir(event_approach_results_path)

    xixi_cc_results_path_no_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results_xixi\noImprInLoop_default_OD\exp_xixi_cc_100')
    xixi_cd_results_path_no_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results_xixi\noImprInLoop_default_OD\exp_xixi_cd_100')

    xixi_cc_results_path_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results_xixi\imprInLoop_adaptive_OD\exp_xixi_cc_100')
    xixi_cd_results_path_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\pm-label-splitting\results_xixi\imprInLoop_adaptive_OD\exp_xixi_cd_100')

    file_paths_event_approach = [join(event_approach_results_path, f) for f in listdir(event_approach_results_path) if
                                 isfile(join(event_approach_results_path, f))]
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

    dfs = []
    for path in file_paths_event_approach:
        dfs.append(pd.read_csv(path))

    df = pd.concat(dfs)
    # df = df.loc[df['use_combined_context'] == False]
    ari, prec, average_max_prec, average_max_ari = get_results(df)
    print('My approach')
    print('ARI')
    print(ari)
    print(average_max_ari)
    print('Precision')
    print(prec)
    print(average_max_prec)

    plt.figure()
    bp = df.boxplot(column=['Precision Align'], grid=False)
    plt.show()

    plt.figure()
    bp = df.boxplot(column=['ARI'], grid=False)
    plt.show()

    plt.figure()
    bp = df.boxplot(by=['use_combined_context', 'distance_metric', 'window_size', 'threshold'], column=['Precision Align'], grid=False)
    plt.show()

    plt.figure()
    bp = df.boxplot(by=['use_combined_context', 'distance_metric', 'window_size', 'threshold'], column=['ARI'], grid=False)
    plt.show()

    dfs_xixi_cc = []
    for path in file_paths_xixi_cc:
        dfs_xixi_cc.append(pd.read_csv(path))
    df_xixi_cc = pd.concat(dfs_xixi_cc)
    df_xixi_cc['Name'] = df_xixi_cc['Folder'] + '/' + df_xixi_cc['Log']
    print('Base Data:')
    print(df_xixi_cc['Original Model Precision'].mean())
    print(df_xixi_cc['Precise Log Precision '].mean())
    print(df_xixi_cc['Unrefined Log Precision'].mean())
    print(df_xixi_cc['Xixi Log Precision'].mean())

    df_xixi_cc = df_xixi_cc.loc[df_xixi_cc['Unfolding Threshold'] > 0.5]

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

    ari, prec, average_max_prec, average_max_ari = get_results_xixi(df_xixi_cc)

    print('Xixi CC')
    print('ARI')
    print(ari)
    print(average_max_ari)
    print('Precision')
    print(prec)
    print(average_max_prec)

    dfs_xixi_cd = []
    for path in file_paths_xixi_cd:
        dfs_xixi_cd.append(pd.read_csv(path))
    df_xixi_cd = pd.concat(dfs_xixi_cd)
    df_xixi_cd['Name'] = df_xixi_cd['Folder'] + '/' + df_xixi_cd['Log']

    # df_xixi_cd = df_xixi_cd.loc[df_xixi_cd['Unfolding Threshold'] > 0.5]

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

    ari, prec, average_max_prec, average_max_ari = get_results_xixi(df_xixi_cd)
    print('Xixi CD')
    print('ARI')
    print(ari)
    print(average_max_ari)
    print('Precision')
    print(prec)
    print(average_max_prec)


def get_results(df):
    # print(df.groupby(['Name'])['ARI'].max())
    return df['ARI'].mean(), df['Precision Align'].mean(), df.groupby(['Name'])['Precision Align'].max().mean(), \
           df.groupby(['Name'])['ARI'].max().mean()


def get_results_xixi(df):
    # print(df.groupby(['Log'])['Refined Log ARI'].max())
    # print('Mean:')
    # print(df.groupby(['Log'])['Refined Log ARI'].max().mean())

    return df['Refined Log ARI'].mean(), df['Refined Log Precision'].mean(), df.groupby(['Name'])[
        'Refined Log Precision'].max().mean(), df.groupby(['Name'])['Refined Log ARI'].max().mean()


main()
