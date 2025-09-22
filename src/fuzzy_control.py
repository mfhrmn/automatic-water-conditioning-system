# fuzzy_control.py

# Membership function boundaries (triangle MF)
error_mf_bounds = {
    'Very Cold': (-100, -10, -5),
    'Cold': (-10, -5, 0),
    'Normal': (-5, 0, 5),
    'Hot': (0, 5, 10),
    'Very Hot': (5, 10, 100)
}

delta_error_mf_bounds = {
    'Decreasing': (-100, -5, 0),
    'Stable': (-2, 0, 2),
    'Increasing': (0, 5, 100)
}

# Output crisp values for Rasio (%)
output_values = {
    'Sangat Tinggi': 0,
    'Tinggi': 10,
    'Agak Tinggi': 25,
    'Sedang Tinggi': 35,
    'Sedang': 50,
    'Sedang Rendah': 65,
    'Rendah': 75,
    'Sangat Rendah': 90,
    'Minimum': 100
}

# Fuzzy rules as per your specification
rules = {
    ('Very Cold', 'Decreasing'): 'Sangat Tinggi',
    ('Very Cold', 'Stable'): 'Sangat Tinggi',
    ('Very Cold', 'Increasing'): 'Tinggi',
    ('Cold', 'Decreasing'): 'Tinggi',
    ('Cold', 'Stable'): 'Agak Tinggi',
    ('Cold', 'Increasing'): 'Sedang Tinggi',
    ('Normal', 'Decreasing'): 'Sedang Tinggi',
    ('Normal', 'Stable'): 'Sedang', 
    ('Normal', 'Increasing'): 'Sedang Rendah',
    ('Hot', 'Decreasing'): 'Sedang Rendah',
    ('Hot', 'Stable'): 'Rendah',
    ('Hot', 'Increasing'): 'Sangat Rendah',
    ('Very Hot', 'Decreasing'): 'Sangat Rendah',
    ('Very Hot', 'Stable'): 'Minimum',
    ('Very Hot', 'Increasing'): 'Minimum'
}

def triangle_mf(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif b <= x < c:
        return (c - x) / (c - b)
    else:
        return 0.0

def mf_error(x):
    memberships = {}
    for label, (a, b, c) in error_mf_bounds.items():
        memberships[label] = triangle_mf(x, a, b, c)
    return memberships

def mf_delta_error(x):
    memberships = {}
    for label, (a, b, c) in delta_error_mf_bounds.items():
        memberships[label] = triangle_mf(x, a, b, c)
    return memberships

def fuzzy_sugeno(error, delta_error):
    error_memberships = mf_error(error)
    delta_error_memberships = mf_delta_error(delta_error)

    numerator = 0.0
    denominator = 0.0

    for e_label, e_val in error_memberships.items():
        if e_val == 0:
            continue
        for d_label, d_val in delta_error_memberships.items():
            if d_val == 0:
                continue
            weight = min(e_val, d_val)
            output_label = rules.get((e_label, d_label))
            if output_label:
                z = output_values[output_label]
                numerator += weight * z
                denominator += weight

    if denominator == 0:
        # No rule fired, return 0 or some default safe value
        return 0
    return numerator / denominator
