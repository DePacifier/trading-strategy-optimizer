import random


def clamp_value(val, spec):
    """Clamp *val* to the range specified in *spec* and apply any step.

    For ``type`` ``'list'`` the *val* represents an index into ``spec['values']``
    and will be clamped to the valid range of indices.  The index is returned
    without decoding so optimisers can continue to operate on numeric values.
    """

    if spec['type'] == 'list':
        values = spec.get('values', [])
        if not values:
            raise ValueError("spec['values'] must contain at least one item")
        idx = int(round(val))
        return min(max(idx, 0), len(values) - 1)

    low, high = spec['low'], spec['high']
    step = spec.get('step')
    if step is not None:
        if step <= 0:
            raise ValueError("spec['step'] must be positive")
        val = low + round((val - low) / step) * step
    if spec['type'] == 'int':
        val = int(round(val))
    else:
        val = float(val)
    val = min(max(val, low), high)
    if step is not None:
        # Ensure clamped value respects step boundaries after rounding
        val = low + round((val - low) / step) * step
        if spec['type'] == 'int':
            val = int(round(val))
    if spec['type'] == 'float':
        decimals = spec.get('decimals', 2)
        val = round(val, decimals)
        val = min(max(val, low), high)
    return val


def sample_value(spec):
    """Return a random value respecting type, range and step."""

    if spec['type'] == 'list':
        values = spec.get('values', [])
        if not values:
            raise ValueError("spec['values'] must contain at least one item")
        return random.randint(0, len(values) - 1)

    low, high = spec['low'], spec['high']
    step = spec.get('step')
    if step is not None:
        if step <= 0:
            raise ValueError("spec['step'] must be positive")
        count = int(round((high - low) / step))
        values = [low + i * step for i in range(count + 1)]
        val = random.choice(values)
    elif spec['type'] == 'int':
        val = random.randint(low, high)
    else:
        val = random.uniform(low, high)
    return clamp_value(val, spec)


def decode_value(val, spec):
    """Decode *val* according to ``spec`` if it represents a list index."""
    if spec['type'] == 'list':
        values = spec.get('values', [])
        if not values:
            raise ValueError("spec['values'] must contain at least one item")
        idx = int(round(val))
        idx = min(max(idx, 0), len(values) - 1)
        return values[idx]
    return val
