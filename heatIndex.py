def heat_index(temperature, humidity):
    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -6.83783e-3
    c6 = -5.481717e-2
    c7 = 1.22874e-3
    c8 = 8.5282e-4
    c9 = -1.99e-6

    T = temperature
    RH = humidity / 100.0

    # Обчислення температури за формулою Steadman
    heat_index = (c1 + (c2 * T) + (c3 * RH) + (c4 * T * RH) +
                  (c5 * T ** 2) + (c6 * RH ** 2) + (c7 * T ** 2 * RH) +
                  (c8 * T * RH ** 2) + (c9 * T ** 2 * RH ** 2))

    return round(heat_index, 1)