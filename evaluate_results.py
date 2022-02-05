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

    variant_approach_results_path_no_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\real_logs\event_based_approach_new\noImprInLoop\results')

    variant_approach_results_path_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\real_logs\event_based_approach_new\imprInLoop\results')

    event_approach_results_path_no_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\real_logs\event_based_approach_events\noImprInLoop\results')

    event_approach_results_path_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\real_logs\event_based_approach_events\imprInLoop\results')

    listdir(variant_approach_results_path_no_impr_loop)

    xixi_cc_results_path_no_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\real_logs\xixi\xixi_no_impr_in_loop\exp_xixi_cc_200')
    xixi_cd_results_path_no_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\real_logs\xixi\xixi_no_impr_in_loop\exp_xixi_cd_200')

    xixi_cc_results_path_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\real_logs\xixi\xixi_impr_in_loop\exp_xixi_cc_200')
    xixi_cd_results_path_impr_loop = Path(
        r'C:\Users\Jonas\Desktop\real_logs\xixi\xixi_impr_in_loop\exp_xixi_cd_200')

    file_paths_variant_approach_no_impr_loop = [join(variant_approach_results_path_no_impr_loop, f) for f in
                                                listdir(variant_approach_results_path_no_impr_loop) if
                                                isfile(join(variant_approach_results_path_no_impr_loop, f))]

    file_paths_variant_approach_impr_loop = [join(variant_approach_results_path_impr_loop, f) for f in
                                             listdir(variant_approach_results_path_impr_loop) if
                                             isfile(join(variant_approach_results_path_impr_loop, f))]

    file_paths_event_approach_no_impr_loop = [join(event_approach_results_path_no_impr_loop, f) for f in
                                                listdir(event_approach_results_path_no_impr_loop) if
                                                isfile(join(event_approach_results_path_no_impr_loop, f))]

    file_paths_event_approach_impr_loop = [join(event_approach_results_path_impr_loop, f) for f in
                                             listdir(event_approach_results_path_impr_loop) if
                                             isfile(join(event_approach_results_path_impr_loop, f))]

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


    sets_num = 2

    if sets_num == 0:
        file_paths_xixi_cc = file_paths_xixi_cc_impr_loop + file_paths_xixi_cc_no_impr_loop
        file_paths_xixi_cd = file_paths_xixi_cd_impr_loop + file_paths_xixi_cd_no_impr_loop
        file_paths_variant_approach = file_paths_variant_approach_no_impr_loop + file_paths_variant_approach_impr_loop
        file_paths_event_approach = file_paths_event_approach_no_impr_loop + file_paths_event_approach_impr_loop
    elif sets_num == 1:
        file_paths_xixi_cc = file_paths_xixi_cc_impr_loop
        file_paths_xixi_cd = file_paths_xixi_cd_impr_loop
        file_paths_variant_approach = file_paths_variant_approach_impr_loop
        file_paths_event_approach = file_paths_event_approach_impr_loop
    else:
        file_paths_xixi_cc = file_paths_xixi_cc_no_impr_loop
        file_paths_xixi_cd = file_paths_xixi_cd_no_impr_loop
        file_paths_variant_approach = file_paths_variant_approach_no_impr_loop
        file_paths_event_approach = file_paths_event_approach_no_impr_loop


    def get_results(df):
        return df['ARI'].mean(), df['Precision Align'].mean(), df.groupby(['Name'])['Precision Align'].max().mean(), \
               df.groupby(['Name'])['ARI'].max().mean(), df['Xixi Precision'].mean(), df.groupby(['Name'])[
                   'Xixi Precision'].max().mean()

    def get_results_xixi(df):
        return df['Refined Log ARI'].mean(), df['Refined Log Precision'].mean(), df.groupby(['Name'])[
            'Refined Log Precision'].max().mean(), df.groupby(['Name'])['Refined Log ARI'].max().mean()

    # %%

    dfs_events = []
    for path in file_paths_variant_approach:
        if 'png' in path:
            continue
        temp = pd.read_csv(path)
        # for i in range(166, len(temp), 330):
        #     end = min(len(temp), i + 165)
        #     temp.loc[i:end, 'use_frequency'] = True

        dfs_events.append(temp)

    df_events = pd.DataFrame(np.concatenate([df_temp.values for df_temp in dfs_events]),
                             columns=dfs_events[0].columns)
    models_event_based = {}
    logs_event_based = set(list(df_events['Name']))
    print(logs_event_based)

    for name in logs_event_based:
        split_name = name.split('/')
        models_event_based.setdefault(split_name[0], set()).add(split_name[1])
    print(models_event_based)

    # df_events = df_events.loc[df_events['use_frequency'] == True]
    # df_events = df_events.loc[df_events['window_size'] == 4]
    # df_events = df_events.loc[df_events['distance_metric'] == 'DistanceVariant.MULTISET_DISTANCE']
    # df_events = df_events.loc[df_events['threshold'] < 0.8]
    # df_events = df_events.loc[df_events['threshold'] < 0.8]

    ari, prec, average_max_prec, average_max_ari, xixi_prec, average_xixi_max_prec = get_results(df_events)
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
    print('Xixi ARI')
    print(df_events['Xixi ARI'].mean())
    print(df_events.groupby(['Name'])['Xixi ARI'].max().mean())
    print('Original Precision')
    print(df_events['original_precision'].mean())
    print(df_events.groupby(['Name'])['original_precision'].max().mean())

    # %%

    dfs = []
    for path in file_paths_variant_approach:
        if 'png' in path:
            continue
        temp = pd.read_csv(path)
        # for i in range(166, len(temp), 330):
        #     end = min(len(temp), i + 165)
        #     temp.loc[i:end, 'use_frequency'] = True

        dfs.append(temp)

    df = pd.DataFrame(np.concatenate([df_temp.values for df_temp in dfs]), columns=dfs[0].columns)
    models = {}
    logs = set(list(df['Name']))
    print(logs)

    for name in logs:
        split_name = name.split('/')
        models.setdefault(split_name[0], set()).add(split_name[1])
    print(models)

    # df = df.loc[df['use_frequency'] == True]
    # df = df.loc[df['window_size'] == 4]
    # df = df.loc[df['distance_metric'] == 'DistanceVariant.MULTISET_DISTANCE']
    # df = df.loc[df['threshold'] < 0.8]
    # df = df.loc[df['threshold'] < 0.8]
    df = df.loc[df['Name'].isin(logs_event_based)]


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
    print('Xixi ARI')
    print(df['Xixi ARI'].mean())
    print(df.groupby(['Name'])['Xixi ARI'].max().mean())
    print('Original Precision')
    print(df['original_precision'].mean())
    print(df.groupby(['Name'])['original_precision'].max().mean())


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
    xixi_names = set(list(df_xixi_cc['Name']))

    df_xixi_cc = df_xixi_cc.loc[df_xixi_cc['Name'].isin(logs_event_based)]

    c = 0
    for name in xixi_names:
        if name in logs:
            c += 1
    print("Total logs")
    print(c)

    models = {}
    # print(logs)

    for name in xixi_names:
        split_name = name.split('/')
        models.setdefault(split_name[0], set()).add(split_name[1])

    print('len(xixi_names)')
    print(len(xixi_names))
    print('Models')
    print(models)

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

    df_xixi_cd = df_xixi_cd.loc[df_xixi_cd['Name'].isin(logs_event_based)]

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
    # bp = df.boxplot(column=['ARI'], grid=False)
    plt.boxplot(df['ARI'], positions=[1])
    plt.boxplot(df_events['ARI'], positions=[2])
    plt.boxplot(df_xixi_cc['Refined Log ARI'], positions=[3])
    plt.boxplot(df_xixi_cd['Refined Log ARI'], positions=[4])
    plt.xlabel('Algorithms')
    plt.ylabel('ARI')
    plt.show()

    plt.figure()
    # bp = df.boxplot(column=['ARI'], grid=False)
    plt.boxplot(df['Precision Align'], positions=[1])
    plt.boxplot(df_events['Precision Align'], positions=[2])
    plt.boxplot(df_xixi_cc['Refined Log Precision'], positions=[3])
    plt.boxplot(df_xixi_cd['Refined Log Precision'], positions=[4])
    plt.boxplot(df_xixi_cc['Precise Log Precision '], positions=[5])
    plt.boxplot(df_xixi_cc['Unrefined Log Precision'], positions=[6])
    plt.xlabel('Algorithms')
    plt.ylabel('Precision')
    plt.show()

    plt.figure()
    # bp = df.boxplot(column=['ARI'], grid=False)
    plt.boxplot(df.groupby(['Name'])['Precision Align'].max(), positions=[1])
    plt.boxplot(df_events.groupby(['Name'])['Precision Align'].max(), positions=[2])
    plt.boxplot(df_xixi_cc.groupby(['Name'])['Refined Log Precision'].max(), positions=[3])
    plt.boxplot(df_xixi_cd.groupby(['Name'])['Refined Log Precision'].max(), positions=[4])
    plt.boxplot(df_xixi_cc.groupby(['Name'])['Precise Log Precision '].max(), positions=[5])
    plt.boxplot(df_xixi_cc.groupby(['Name'])['Unrefined Log Precision'].max(), positions=[6])
    plt.xlabel('Algorithms')
    plt.ylabel('Max Precision')
    plt.show()

    plt.figure()
    # bp = df.boxplot(column=['ARI'], grid=False)
    plt.boxplot(df.groupby(['Name'])['ARI'].max(), positions=[1])
    plt.boxplot(df_events.groupby(['Name'])['ARI'].max(), positions=[2])
    plt.boxplot(df_xixi_cc.groupby(['Name'])['Refined Log ARI'].max(), positions=[3])
    plt.boxplot(df_xixi_cd.groupby(['Name'])['Refined Log ARI'].max(), positions=[4])
    plt.xlabel('Algorithms')
    plt.ylabel('Max ARI')
    plt.show()


    plt.figure()
    # bp = df.boxplot(column=['ARI'], grid=False)
    plt.boxplot(df['Simplicity'], positions=[1])
    plt.boxplot(df_events['Simplicity'], positions=[2])
    plt.boxplot(df_xixi_cc['Refined Log Simplicity'], positions=[3])
    plt.boxplot(df_xixi_cd['Refined Log Simplicity'], positions=[4])
    plt.boxplot(df_xixi_cc['Precise Log Simplicity'], positions=[5])
    plt.boxplot(df_xixi_cc['Unrefined Log Simplicity'], positions=[6])
    plt.xlabel('Algorithms')
    plt.ylabel('Simplicity')
    plt.show()

    plt.figure()
    # bp = df.boxplot(column=['ARI'], grid=False)
    plt.boxplot(df.groupby(['Name'])['Simplicity'].max(), positions=[1])
    plt.boxplot(df_events.groupby(['Name'])['Simplicity'].max(), positions=[2])
    plt.boxplot(df_xixi_cc.groupby(['Name'])['Refined Log Simplicity'].max(), positions=[3])
    plt.boxplot(df_xixi_cd.groupby(['Name'])['Refined Log Simplicity'].max(), positions=[4])
    plt.boxplot(df_xixi_cc.groupby(['Name'])['Precise Log Simplicity'].max(), positions=[5])
    plt.boxplot(df_xixi_cc.groupby(['Name'])['Unrefined Log Simplicity'].max(), positions=[6])
    plt.xlabel('Algorithms')
    plt.ylabel('Max Simplicity')
    plt.show()

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
