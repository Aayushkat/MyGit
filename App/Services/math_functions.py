def _fix_rounding(stats: list[dict[str, str | int]])->list[dict[str, str | int]]:
    # Store the fractional remainder
    for stat in stats:
        stat["_remainder"] = stat["percentage"] - int(stat["percentage"])
        stat["percentage"] = int(stat["percentage"])

    # How many percentage points are still needed?
    remaining = 100 - sum(stat["percentage"] for stat in stats)

    # Give extra points to the largest remainders
    stats.sort(key=lambda stat: stat["_remainder"], reverse=True)

    for stat in stats[:remaining]:
        stat["percentage"] += 1

    # Remove the temporary field
    for stat in stats:
        del stat["_remainder"]

    return stats