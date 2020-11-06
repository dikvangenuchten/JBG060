import pandas as pd


def plot_5_pumps_level_to_m3():
    """Plots 5 pumps, level in cm against m3 volume"""
    df = pd.read_csv(f"processed\\Helftheuvel_single_cm_m3.csv")
    ax = df.plot(None, ['m3'])
    pumps = ['Engelerschans', 'Maaspoort', 'Rompert', 'Oude Engelenseweg']
    for pump in pumps:
        df = pd.read_csv(f"processed\\{pump}_single_cm_m3.csv")
        df.plot(None, ['m3'], ax=ax)
    ax.legend(['Helftheuvel', 'Engelerschans', 'Maaspoort', 'Rompert', 'Oude Engelenseweg'])
    ax.set_title("Relation between level and volume for 5 pumps")
    ax.set_xlabel("level in cm")
    ax.set_ylabel("volume in m3")
    ax.figure.savefig('5_pumps_levels_in_cm_to_m3_volume.jpeg', dpi=1000, transparent=True)
