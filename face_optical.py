import sensor
import time
import math
import image

BLOCK_W = 16  # pow2
BLOCK_H = 16  # pow2

sensor.reset()  # Reset and initialize the sensor.
# sensor.set_pixformat(sensor.GRAYSCALE)  # Set pixel format to GRAYSCALE (or RGB565)
# sensor.set_framesize(sensor.B128X128)  # Set frame size to 128x128... (or 128x64)...

# Sensor settings
sensor.set_contrast(3)
sensor.set_gainceiling(16)
# HQVGA and GRAYSCALE are the best for face tracking.
sensor.set_framesize(sensor.HQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)

face_cascade = image.HaarCascade("frontalface", stages=25)

sensor.skip_frames(time=2000)  # Wait for settings take effect.
clock = time.clock()  # Create a clock object to track the FPS.

# Take from the main frame buffer's RAM to allocate a second frame buffer.
# There's a lot more RAM in the frame buffer than in the MicroPython heap.
# However, after doing this you have a lot less RAM for some algorithms...
# So, be aware that it's a lot easier to get out of RAM issues now.
extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.GRAYSCALE)
extra_fb.replace(sensor.snapshot())

while True:
    clock.tick()  # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot()  # Take a picture and return the image.

    objects = img.find_features(face_cascade, threshold=0.75, scale_factor=1.25)
    # Draw objects
    for r in objects:
        img.draw_rectangle(r)

    for y in range(0, sensor.height(), BLOCK_H):
        for x in range(0, sensor.width(), BLOCK_W):
            # For this example we never update the old image to measure absolute change.
            displacement = extra_fb.find_displacement(
                img,
                logpolar=True,
                roi=(x, y, BLOCK_W, BLOCK_H),
                template_roi=(x, y, BLOCK_W, BLOCK_H),
            )

            # Below 0.1 or so (YMMV) and the results are just noise.
            if displacement.response() > 0.1:
                rotation_change = displacement.rotation()
                zoom_amount = displacement.scale()
                pixel_x = (
                    x
                    + (BLOCK_W // 2)
                    + int(math.sin(rotation_change) * zoom_amount * (BLOCK_W // 4))
                )
                pixel_y = (
                    y
                    + (BLOCK_H // 2)
                    + int(math.cos(rotation_change) * zoom_amount * (BLOCK_H // 4))
                )
                img.draw_line(
                    (x + BLOCK_W // 2, y + BLOCK_H // 2, pixel_x, pixel_y), color=255
                )
            else:
                img.draw_line(
                    (
                        x + BLOCK_W // 2,
                        y + BLOCK_H // 2,
                        x + BLOCK_W // 2,
                        y + BLOCK_H // 2,
                    ),
                    color=0,
                )

    print(clock.fps())
