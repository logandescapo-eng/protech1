"""Generate ER and sequence diagrams for the ProTech technical report."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

DIAGRAM_DIR = Path(__file__).resolve().parent.parent / "documentattion" / "report_charts"

BLUE = "#1E3A8A"
BLUE_MID = "#2563EB"
INDIGO = "#4F46E5"
SLATE = "#64748B"
LIGHT = "#DBEAFE"
WHITE = "#FFFFFF"


def _entity_box(ax, x, y, w, h, title, fields, color=BLUE_MID):
    box = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.5, edgecolor=BLUE, facecolor=color, alpha=0.92,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top",
            fontsize=9, fontweight="bold", color=WHITE)
    field_text = "\n".join(fields)
    ax.text(x + 0.12, y + h - 0.45, field_text, ha="left", va="top",
            fontsize=7, color=WHITE, family="monospace")


def _rel_line(ax, x1, y1, x2, y2, label=""):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-", color=SLATE, lw=1.2),
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.08, label, ha="center", va="bottom",
                fontsize=7, color=BLUE, style="italic")


def chart_er_diagram():
    """Entity-relationship diagram of core ProTech models."""
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=150)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.5)
    ax.axis("off")
    ax.set_title("ProTech Entity-Relationship Diagram (Core Schema)",
                 fontsize=13, fontweight="bold", color=BLUE, pad=14)

    # Row 1 — identity
    _entity_box(ax, 0.3, 5.5, 2.0, 1.5, "User", [
        "PK id", "email, user_type", "phone, avatar",
    ])
    _entity_box(ax, 2.8, 5.5, 2.0, 1.5, "Worker", [
        "PK id  FK user_id (1:1)", "skills, service_area",
        "rating, hourly_rate",
    ], INDIGO)
    _entity_box(ax, 5.3, 5.5, 2.2, 1.5, "ServiceCategory", [
        "PK id", "name, description", "icon",
    ], "#0EA5E9")

    # Row 2 — booking & review
    _entity_box(ax, 1.5, 3.2, 2.4, 1.6, "Booking", [
        "PK id", "FK user_id (client)", "FK worker_id",
        "FK service_category_id", "status, payment_status", "price, scheduled_date",
    ])
    _entity_box(ax, 4.5, 3.2, 1.8, 1.3, "Review", [
        "PK id  FK booking_id (1:1)", "FK worker_id", "rating, comment",
    ], INDIGO)

    # Row 3 — escrow
    _entity_box(ax, 0.3, 0.8, 2.0, 1.4, "UserWallet", [
        "PK id  FK user_id (1:1)", "available_balance",
    ], "#0D9488")
    _entity_box(ax, 2.8, 0.8, 2.2, 1.6, "EscrowHold", [
        "PK id  FK booking_id (1:1)", "FK client_id, worker_user_id",
        "amount, platform_fee", "status (held/released/refunded)",
    ])
    _entity_box(ax, 5.5, 0.8, 2.0, 1.3, "WalletTransaction", [
        "PK id  FK user_id", "FK booking_id, escrow_id",
        "transaction_type, amount",
    ], "#0D9488")
    _entity_box(ax, 8.0, 0.8, 1.8, 1.2, "EscrowVault", [
        "PK id=1 (singleton)", "total_held, total_released",
    ])

    # Supporting entities (right column)
    _entity_box(ax, 8.0, 5.5, 2.5, 1.5, "Message", [
        "FK sender_id, receiver_id", "FK booking_id (opt)", "message, is_read",
    ], SLATE)
    _entity_box(ax, 8.0, 3.5, 2.5, 1.3, "Notification", [
        "FK user_id", "title, type, is_read",
    ], SLATE)
    _entity_box(ax, 8.0, 2.0, 2.5, 1.1, "Favorite", [
        "FK user_id, worker_id", "unique (user, worker)",
    ], SLATE)

    # Relationships
    _rel_line(ax, 2.3, 6.25, 2.8, 6.25, "1:1")
    _rel_line(ax, 1.3, 5.5, 2.7, 4.8, "1:N")
    _rel_line(ax, 3.8, 5.5, 2.7, 4.8, "1:N")
    _rel_line(ax, 6.4, 5.5, 3.5, 4.8, "1:N")
    _rel_line(ax, 3.9, 3.2, 4.5, 3.85, "1:1")
    _rel_line(ax, 2.7, 3.2, 3.9, 2.4, "1:1")
    _rel_line(ax, 1.3, 5.5, 1.3, 2.2, "1:1")
    _rel_line(ax, 3.2, 3.2, 3.9, 2.4, "funds")
    _rel_line(ax, 5.0, 1.5, 5.5, 1.5, "logs")
    _rel_line(ax, 1.3, 0.8, 2.8, 1.5, "debit/credit")

    legend = [
        mpatches.Patch(color=BLUE_MID, label="users app"),
        mpatches.Patch(color=INDIGO, label="profiles / reviews"),
        mpatches.Patch(color="#0D9488", label="escrow app"),
    ]
    ax.legend(handles=legend, loc="lower left", fontsize=8, framealpha=0.9)

    fig.tight_layout()
    path = DIAGRAM_DIR / "er_diagram.png"
    fig.savefig(path, facecolor=WHITE, bbox_inches="tight")
    plt.close(fig)
    return path


def chart_escrow_sequence():
    """UML-style sequence diagram for booking and escrow release."""
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("Escrow Payment Sequence Diagram",
                 fontsize=13, fontweight="bold", color=BLUE, pad=14)

    actors = [
        ("Client\n(browser)", 1.0),
        ("Django\nViews", 3.0),
        ("escrow/\nservices.py", 5.2),
        ("PostgreSQL\n(database)", 7.5),
        ("Worker\n(browser)", 9.0),
    ]
    y_top = 7.2
    for name, x in actors:
        ax.plot([x, x], [0.5, y_top], color=SLATE, linestyle="--", linewidth=1)
        ax.text(x, y_top + 0.15, name, ha="center", va="bottom",
                fontsize=8, fontweight="bold", color=BLUE)

    steps = [
        (1.0, 3.0, 6.6, "POST /wallet/deposit", BLUE_MID),
        (3.0, 7.5, 6.2, "INSERT UserWallet, WalletTransaction", SLATE),
        (1.0, 3.0, 5.8, "POST /book/ — create Booking (pending)", BLUE_MID),
        (3.0, 7.5, 5.4, "INSERT Booking", SLATE),
        (1.0, 3.0, 5.0, "POST /escrow/ — fund escrow", BLUE_MID),
        (3.0, 5.2, 4.6, "fund_escrow(booking)", INDIGO),
        (5.2, 7.5, 4.2, "TXN: debit wallet, INSERT EscrowHold", SLATE),
        (9.0, 3.0, 3.6, "POST complete booking", BLUE_MID),
        (3.0, 5.2, 3.2, "release_escrow(booking)", INDIGO),
        (5.2, 7.5, 2.8, "TXN: fee calc, credit worker wallet", SLATE),
        (3.0, 1.0, 2.4, "Redirect — job complete", BLUE_MID),
        (5.2, 7.5, 2.0, "UPDATE EscrowVault totals", SLATE),
    ]

    for x1, x2, y, label, color in steps:
        ax.annotate(
            "", xy=(x2, y), xytext=(x1, y),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.3),
        )
        mx = (x1 + x2) / 2
        ax.text(mx, y + 0.12, label, ha="center", va="bottom",
                fontsize=6.5, color=color)

    # Return arrow for response
    ax.annotate(
        "", xy=(1.0, 1.6), xytext=(3.0, 1.6),
        arrowprops=dict(arrowstyle="->", color=SLATE, lw=1, linestyle="dashed"),
    )
    ax.text(2.0, 1.75, "HTTP response", ha="center", fontsize=6.5, color=SLATE)

    ax.text(5.0, 0.35,
            "All monetary mutations use Decimal types and database transactions (atomic)",
            ha="center", fontsize=8, color=SLATE, style="italic")

    fig.tight_layout()
    path = DIAGRAM_DIR / "escrow_sequence.png"
    fig.savefig(path, facecolor=WHITE, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_all_diagrams():
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    return {
        "er": chart_er_diagram(),
        "sequence": chart_escrow_sequence(),
    }


if __name__ == "__main__":
    paths = generate_all_diagrams()
    for k, v in paths.items():
        print(k, v)
