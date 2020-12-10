import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from knitSensorNotif import BLEDevice
from collections import deque

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

maxlength = 10
xs = deque(maxlen=maxlength)
ys = deque(maxlen=maxlength)
yd = [deque(maxlen=maxlength), deque(maxlen=maxlength), deque(maxlen=maxlength), deque(maxlen=maxlength)]
# This function is called periodically from FuncAnimation
def animate(i, xs, ys):

    # Read temperature (Celsius) from TMP102
    addr, mv = KneeBrace.readSensors()
    print(mv)
    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))


    # Draw x and y lists
    ax.clear()
    for i in range(4):
        yd[i].append(mv[i])
        ax.plot(xs, yd[i])

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    # plt.title('TMP102 Temperature over Time')
    # plt.ylabel('Temperature (deg C)')




KneeBrace = BLEDevice()
if KneeBrace.scanAndConnect():
    try:
        # Set up plot to call animate() function periodically
        ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=0.0001)
        plt.show()
    except KeyboardInterrupt:
        KneeBrace.disconnect()
        quit()