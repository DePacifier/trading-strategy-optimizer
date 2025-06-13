import random


def clamp_value(val, spec):
    """Clamp *val* to the range specified in *spec* and apply any step."""
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
    return val


def sample_value(spec):
    """Return a random value respecting type, range and step."""
    low, high = spec['low'], spec['high']
    step = spec.get('step')
    if step is not None:
        if step <= 0:
            raise ValueError("spec['step'] must be positive")
        count = int(round((high - low) / step))
        values = [low + i * step for i in range(count + 1)]
        return random.choice(values)
    if spec['type'] == 'int':
        return random.randint(low, high)
    return random.uniform(low, high)
