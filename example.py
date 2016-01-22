from noise import snoise2 # pip install noise
from png import Writer # pip install pypng
import random

ELEV_SEA = 0.25

def noise(width, height, seed, freq):
    return [[snoise2(x / freq * 2, y / freq * 2, 1, base=seed) for x in range(width)] for y in range(height)]


def draw_map(width, height, map, filename, pixel_function):
    writer = Writer(width, height)
    pixels = [reduce(lambda x, y: x+y, [pixel_function(elev) for elev in row]) for row in map]
    with open(filename, 'w') as f:
        writer.write(f, pixels)


def draw_bw_map(width, height, map, filename):

    def elev_to_pixel(elev):
        v = (elev + 1.0) * 255.0/2.0
        return v, v, v

    return draw_map(width, height, map, filename, elev_to_pixel)


def gradient(value, low, high, low_color, high_color):
    lr, lg, lb = low_color
    hr, hg, hb = high_color
    _range = float(high - low)
    _x = float(value - low) / _range
    _ix = 1.0 - _x
    r = int(lr * _ix + hr * _x)
    g = int(lg * _ix + hg * _x)
    b = int(lb * _ix + hb * _x)
    return r, g, b


def erode(width, height, map, n_droplets):

    EROSION = 0.001
    MIN_EROSION = EROSION / 100.0

    def spread(x, y, erosion):
        lower = []
        sum_diff = 0.0
        for ax in range(max(0, x - 1), min(width - 1, x + 2)):
            for ay in range(max(0, y - 1), min(height - 1, y + 2)):
                elev = map[ay][ax]
                if elev < map[y][x]:
                    sum_diff += (map[y][x] - elev)
                    lower.append({'diff': map[y][x] - elev, 'x': ax, 'y': ay})
        if sum_diff > 0.0:
            for l in lower:
                e = erosion * 1.2 * (l['diff']/sum_diff)
                #print("ER " + str(e))
                droplet(l['x'], l['y'], e)

    def droplet(x, y, erosion):
        if map[y][x] < ELEV_SEA:
            return
        if erosion < MIN_EROSION:
            return
        map[y][x] -= erosion
        spread(x, y, erosion)

    for d in range(n_droplets):
        if d % 100 == 0:
            print(d)
        droplet(random.randint(0, width-1), random.randint(0, height-1), EROSION)


def draw_color_map(width, height, map, filename):

    ELEV_MIN = -1.0
    ELEV_HILL = 0.65
    ELEV_MOUNTAIN = 1.0

    COAST_COLOR = (203, 237, 128)
    HILL_COLOR = (65, 69, 28)
    MOUNTAIN_COLOR = (226, 227, 218)
    SHALLOW_SEA_COLOR = (128, 237, 235)
    DEEP_SEA_COLOR = (2, 69, 92)

    def elev_to_pixel(elev):
        if elev > ELEV_HILL:
            return gradient(elev, ELEV_HILL, ELEV_MOUNTAIN, HILL_COLOR, MOUNTAIN_COLOR)
        elif elev > ELEV_SEA:
            return gradient(elev, ELEV_SEA, ELEV_HILL, COAST_COLOR, HILL_COLOR)
        else:
            return gradient(elev, ELEV_MIN, ELEV_SEA, DEEP_SEA_COLOR, SHALLOW_SEA_COLOR)

    return draw_map(width, height, map, filename, elev_to_pixel)


def combine_maps(width, height, maps_and_factors):

    def calc_elev(x, y):
        total = reduce(lambda x, y: x+y, [map[y][x] * factor for map, factor in maps_and_factors])
        return total / sum_factors

    sum_factors = reduce(lambda x, y: x + y, [f for m, f in maps_and_factors])
    return [[calc_elev(x, y) for x in range(width)] for y in range(height)]


def main():
    map1 = noise(512, 512, 77777, 512.0)
    draw_bw_map(512, 512, map1, "example1.png")
    map2 = noise(512, 512, 77777, 256.0)
    draw_bw_map(512, 512, map2, "example2.png")
    map3 = noise(512, 512, 77777, 128.0)
    draw_bw_map(512, 512, map3, "example3.png")
    map4 = noise(512, 512, 77777, 32.0)
    draw_bw_map(512, 512, map4, "example4.png")
    map_combined = combine_maps(512, 512, [(map1, 8), (map2, 4), (map3, 2), (map4, 1)])
    draw_bw_map(512, 512, map_combined, "example_combined.png")
    draw_color_map(512, 512, map_combined, "example_combined_color.png")
    erode(512, 512, map_combined, 100000)
    draw_color_map(512, 512, map_combined, "example_combined_color_eroded.png")

if __name__ == "__main__":
    random.seed(77777)
    main()
