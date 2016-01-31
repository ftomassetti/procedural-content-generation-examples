from noise import snoise2 # pip install noise
from png import Writer # pip install pypng

ELEV_SEA = 0.25
ELEV_HILL = 0.65


def noise(width, height, seed, period):
    return [[snoise2(x / period * 2, y / period * 2, 1, base=seed) for x in range(width)] for y in range(height)]


def draw_map(width, height, map, filename, pixel_function):
    """
    Generic function to draw maps with PyPNG
    """
    writer = Writer(width, height)
    pixels = [reduce(lambda x, y: x + y, [pixel_function(elev) for elev in row]) for row in map]
    with open(filename, 'w') as f:
        writer.write(f, pixels)


def draw_bw_map(width, height, map, filename):
    """
    Produce black and white pixels
    """

    def elev_to_pixel(elev):
        v = (elev + 1.0) * 255.0/2.0
        v = min(255, max(0, v))
        return v, v, v

    return draw_map(width, height, map, filename, elev_to_pixel)


def gradient(value, low, high, low_color, high_color):
    """
    Mix two colors according to the given proportion
    """
    lr, lg, lb = low_color
    hr, hg, hb = high_color
    _range = float(high - low)
    _x = float(value - low) / _range
    _ix = 1.0 - _x
    r = int(lr * _ix + hr * _x)
    g = int(lg * _ix + hg * _x)
    b = int(lb * _ix + hb * _x)
    r = min(255, max(0, r))
    g = min(255, max(0, g))
    b = min(255, max(0, b))
    return r, g, b


def draw_color_map(width, height, map, filename):
    """
    Produce a maps with colors which depend on the elevation
    """

    ELEV_MIN = -1.0
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
    """
    Combine different maps using a specific weight for each of them
    """

    def calc_elev(x, y):
        total = reduce(lambda x, y: x+y, [map[y][x] * factor for map, factor in maps_and_factors])
        return total / sum_factors

    sum_factors = reduce(lambda x, y: x + y, [f for m, f in maps_and_factors])
    return [[calc_elev(x, y) for x in range(width)] for y in range(height)]


def main():
    width = 512
    height = 512
    seed = 77777

    map1 = noise(width, height, seed, 512.0)
    draw_bw_map(width, height, map1, "noise_period512.png")

    map2 = noise(width, height, seed, 256.0)
    draw_bw_map(width, height, map2, "noise_period256.png")

    map3 = noise(width, height, seed, 128.0)
    draw_bw_map(width, height, map3, "noise_period128.png")

    map4 = noise(width, height, seed, 64.0)
    draw_bw_map(width, height, map4, "noise_period64.png")

    map5 = noise(width, height, seed, 32.0)
    draw_bw_map(width, height, map5, "noise_period32.png")

    map6 = noise(width, height, seed, 16.0)
    draw_bw_map(width, height, map6, "noise_period16.png")

    map7 = noise(width, height, seed, 8.0)
    draw_bw_map(width, height, map7, "noise_period8.png")

    map_combined = combine_maps(width, height, [(map1, 64), (map2, 32), (map3, 16), (map4, 8), (map5, 4), (map6, 2), (map7, 1)])
    draw_bw_map(width, height, map_combined, "example_combined.png")

    draw_color_map(width, height, map_combined, "example_combined_color.png")


if __name__ == "__main__":
    main()
