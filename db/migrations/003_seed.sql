INSERT INTO items (id, name, description, weight_kg, price, quantity, half_of, is_active) VALUES
    (1, 'Crimson Sweet',        'classic striped, sweet and juicy', 8.00,  24.90, 120, NULL, true),
    (2, 'Sugar Baby',           'mini, dark rind',                  3.00,  14.50,  60, NULL, true),
    (3, 'Yellow Doll',          'yellow flesh, honey sweet',        4.00,  19.90,  25, NULL, true),
    (4, 'Seedless Jubilee',     'seedless, large',                  10.00, 32.00,   0, NULL, true),
    (5, 'Crimson Sweet - Half', 'half of Crimson Sweet',            4.00,  14.94,  30, 1,    true),
    (6, 'Moon and Stars',       'heirloom, spotted rind',           6.00,  21.00,  10, NULL, false);

SELECT setval(pg_get_serial_sequence('items', 'id'), 6);
