from beset._interval_data import Bound


def interval_str(x: Bound[object] | None, y: Bound[object] | None, empty: bool) -> str:
    if empty:
        return "EMPTY"

    match x:
        case None:
            left = "<-Inf"
        case (value, sinister):
            left = ("<" if sinister else "[") + str(value)

    match y:
        case None:
            right = "Inf>"
        case (value, sinister):
            right = str(value) + ("]" if sinister else ">")

    return f"{left} : {right}"  # pyrefly:ignore[unbound-name]
