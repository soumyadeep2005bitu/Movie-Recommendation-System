def convert_runtime(minutes):

    if minutes == 0:
        return "N/A"

    hours = minutes // 60
    mins = minutes % 60

    if hours > 0:
        return f"{hours} hr {mins} min"
    else:
        return f"{mins} min"