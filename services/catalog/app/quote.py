from typing import Any, Mapping, Sequence

from app.schemas import QuoteLineIn, QuoteLineOut, QuoteOut


class QuoteError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def merge_lines(lines: Sequence[QuoteLineIn]) -> dict[int, int]:
    merged: dict[int, int] = {}
    for line in lines:
        merged[line.item_id] = merged.get(line.item_id, 0) + line.quantity
    return merged


def build_quote(rows: Sequence[Mapping[str, Any]], lines: Sequence[QuoteLineIn]) -> QuoteOut:
    by_id = {row["id"]: row for row in rows}
    out_lines: list[QuoteLineOut] = []

    for item_id, requested in merge_lines(lines).items():
        row = by_id.get(item_id)
        if row is None:
            raise QuoteError("unknown_item", f"item {item_id} does not exist")
        if requested >= row["quantity"]:
            raise QuoteError(
                "insufficient_stock",
                f"only {row['quantity']} of '{row['name']}' available",
            )
        unit = float(row["price"])
        out_lines.append(
            QuoteLineOut(
                item_id=item_id,
                name=row["name"],
                unit_price=unit,
                quantity=requested,
                line_total=unit * requested,
            )
        )

    return QuoteOut(lines=out_lines, total=sum(line.line_total for line in out_lines))
