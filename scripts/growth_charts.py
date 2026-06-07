"""Generate growth projection charts for the ProTech technical report."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

CHART_DIR = Path(__file__).resolve().parent.parent / "documentattion" / "report_charts"

BLUE = "#2563EB"
INDIGO = "#4F46E5"
SKY = "#0EA5E9"
TEAL = "#0D9488"
AMBER = "#D97706"
SLATE = "#64748B"
LIGHT = "#DBEAFE"

MONTHS = np.arange(1, 25)
MONTH_LABELS = [f"Month {m}" for m in MONTHS]
# Show every 3rd label on x-axis for readability
XTICKS = list(range(0, 24, 3))
XTICK_LABELS = [MONTH_LABELS[i] for i in XTICKS]


def _compound_growth(start: float, monthly_rates: list) -> list:
    values = [start]
    for rate in monthly_rates:
        values.append(values[-1] * (1 + rate))
    return values[1:]


def build_projections():
    """Deterministic 24-month post-launch projections (illustrative)."""
    # Launch phase → acceleration → maturity
    traffic_rates = [0.18, 0.16, 0.15, 0.14, 0.13, 0.12]  # M1-6
    traffic_rates += [0.11, 0.10, 0.10, 0.09, 0.09, 0.08]  # M7-12
    traffic_rates += [0.07, 0.07, 0.06, 0.06, 0.05, 0.05]  # M13-18
    traffic_rates += [0.04, 0.04, 0.04, 0.03, 0.03, 0.03]  # M19-24

    visitors = _compound_growth(650, traffic_rates)
    page_views = [int(v * 3.6) for v in visitors]  # ~3.6 pages per visitor
    mau = [int(v * 0.62) for v in visitors]  # 62% of visitors return within month

    client_rates = [0.14] * 6 + [0.10] * 6 + [0.07] * 6 + [0.04] * 6
    worker_rates = [0.12] * 6 + [0.09] * 6 + [0.06] * 6 + [0.035] * 6

    clients = [int(x) for x in _compound_growth(95, client_rates)]
    workers = [int(x) for x in _compound_growth(38, worker_rates)]

    job_rates = [0.16] * 6 + [0.11] * 6 + [0.08] * 6 + [0.045] * 6
    completed_jobs = [int(x) for x in _compound_growth(22, job_rates)]
    avg_job_value = [135 + min(m * 1.8, 45) for m in range(24)]  # rises with commercial jobs
    gmv = [completed_jobs[i] * avg_job_value[i] for i in range(24)]

    commission_mrr = [gmv[i] * 0.048 for i in range(24)]  # blended ~4.8% take rate
    # Subscription adoption ramps after month 6
    sub_penetration = [0, 0, 0, 0, 0, 0.08, 0.12, 0.15, 0.18, 0.20, 0.22, 0.24,
                       0.26, 0.28, 0.30, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.38, 0.39]
    prof_share, prem_share = 0.62, 0.38
    subscription_mrr = [
        workers[i] * sub_penetration[i] * (prof_share * 29 + prem_share * 59)
        for i in range(24)
    ]
    total_mrr = [commission_mrr[i] + subscription_mrr[i] for i in range(24)]

    return {
        "visitors": visitors,
        "page_views": page_views,
        "mau": mau,
        "clients": clients,
        "workers": workers,
        "completed_jobs": completed_jobs,
        "gmv": gmv,
        "commission_mrr": commission_mrr,
        "subscription_mrr": subscription_mrr,
        "total_mrr": total_mrr,
    }


def _style_axes(ax, title, ylabel, xlabel=""):
    ax.set_title(title, fontsize=13, fontweight="bold", color="#1E3A8A", pad=12)
    ax.set_ylabel(ylabel, fontsize=10, color=SLATE)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=SLATE)
    ax.set_xticks([MONTHS[i] for i in XTICKS])
    ax.set_xticklabels([MONTH_LABELS[i] for i in XTICKS], fontsize=8, rotation=0)
    ax.grid(True, alpha=0.35, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def chart_traffic(data):
    fig, ax1 = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    ax1.fill_between(MONTHS, data["visitors"], alpha=0.25, color=BLUE)
    ax1.plot(MONTHS, data["visitors"], color=BLUE, linewidth=2.5, marker="o", markersize=4, label="Monthly visitors")
    ax1.plot(MONTHS, data["mau"], color=INDIGO, linewidth=2, linestyle="--", marker="s", markersize=3, label="Monthly active users")
    _style_axes(ax1, "ProTech Traffic Growth Projection (24 Months)", "Users / Visits")
    ax1.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    ax2 = ax1.twinx()
    ax2.plot(MONTHS, data["page_views"], color=SKY, linewidth=1.8, alpha=0.85, label="Page views")
    ax2.set_ylabel("Page views", fontsize=10, color=SKY)
    ax2.tick_params(axis="y", labelcolor=SKY)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x/1000)}k" if x >= 1000 else f"{int(x)}"))
    ax2.spines["right"].set_visible(True)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8, framealpha=0.9)

    fig.tight_layout()
    path = CHART_DIR / "traffic_growth.png"
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def chart_users(data):
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    ax.fill_between(MONTHS, data["clients"], alpha=0.3, color=BLUE, label="_nolegend_")
    ax.fill_between(MONTHS, data["workers"], alpha=0.35, color=TEAL, label="_nolegend_")
    ax.plot(MONTHS, data["clients"], color=BLUE, linewidth=2.5, marker="o", markersize=4, label="Registered clients")
    ax.plot(MONTHS, data["workers"], color=TEAL, linewidth=2.5, marker="s", markersize=4, label="Registered workers")
    total = [data["clients"][i] + data["workers"][i] for i in range(24)]
    ax.plot(MONTHS, total, color=INDIGO, linewidth=2, linestyle=":", label="Total accounts")
    _style_axes(ax, "Registered User Base Growth (24 Months)", "Accounts")
    ax.legend(loc="upper left", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    path = CHART_DIR / "user_growth.png"
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def chart_revenue(data):
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    comm = np.array(data["commission_mrr"])
    subs = np.array(data["subscription_mrr"])
    ax.bar(MONTHS, comm, color=BLUE, alpha=0.85, label="Commission revenue", width=0.72)
    ax.bar(MONTHS, subs, bottom=comm, color=INDIGO, alpha=0.85, label="Subscription revenue", width=0.72)
    ax.plot(MONTHS, data["total_mrr"], color=AMBER, linewidth=2.5, marker="D", markersize=4, label="Total MRR")
    _style_axes(ax, "Monthly Recurring Revenue Growth (24 Months)", "USD ($)")
    ax.legend(loc="upper left", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${int(x/1000)}k" if x >= 1000 else f"${int(x)}"))
    fig.tight_layout()
    path = CHART_DIR / "revenue_growth.png"
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def chart_bookings_gmv(data):
    fig, ax1 = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    ax1.bar(MONTHS, data["completed_jobs"], color=SKY, alpha=0.75, width=0.7, label="Completed bookings")
    _style_axes(ax1, "Marketplace Activity: Bookings & GMV (24 Months)", "Completed jobs")
    ax1.legend(loc="upper left", fontsize=9)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    ax2 = ax1.twinx()
    ax2.plot(MONTHS, [g / 1000 for g in data["gmv"]], color=AMBER, linewidth=2.5, marker="o", markersize=4, label="GMV ($ thousands)")
    ax2.set_ylabel("GMV ($ thousands)", fontsize=10, color=AMBER)
    ax2.tick_params(axis="y", labelcolor=AMBER)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)
    fig.tight_layout()
    path = CHART_DIR / "bookings_gmv_growth.png"
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def chart_revenue_mix_evolution(data):
    """Line chart: % of MRR from subscriptions over time."""
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=150)
    total = np.array(data["total_mrr"])
    subs_pct = [100 * data["subscription_mrr"][i] / total[i] if total[i] else 0 for i in range(24)]
    comm_pct = [100 - subs_pct[i] for i in range(24)]
    ax.stackplot(MONTHS, comm_pct, subs_pct, colors=[BLUE, INDIGO], alpha=0.75, labels=["Commission %", "Subscription %"])
    _style_axes(ax, "Revenue Mix Evolution (% of Total MRR)", "Share of MRR (%)")
    ax.set_ylim(0, 100)
    ax.legend(loc="center right", fontsize=9)
    fig.tight_layout()
    path = CHART_DIR / "revenue_mix_evolution.png"
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def generate_all_charts():
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    data = build_projections()
    return {
        "traffic": chart_traffic(data),
        "users": chart_users(data),
        "revenue": chart_revenue(data),
        "bookings": chart_bookings_gmv(data),
        "mix": chart_revenue_mix_evolution(data),
        "data": data,
    }


if __name__ == "__main__":
    paths = generate_all_charts()
    for k, v in paths.items():
        if k != "data":
            print(k, v)
