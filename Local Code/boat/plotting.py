import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

points3d = []
ani = None

def set_points3d(zed_object_data):
    global points3d
    points = []
    for obj in zed_object_data.object_list:
        points.append(obj.position)
    points3d = points

def plot_points3d():
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # ax.set_xlim(-3, 3)
    # ax.set_ylim(-3, 3)

    def animate(i):
        ax.clear()
        ax.set_xlim(-5, 5)  # Set x-axis limits
        ax.set_ylim(0, 10)  # Set y-axis limits
        if points3d:
            xs, zs = zip(*[(p[0], p[2]) for p in points3d])
            ax.scatter(xs, zs)

    global ani
    ani = FuncAnimation(plt.gcf(), animate, interval=50, cache_frame_data=False)
    plt.show()