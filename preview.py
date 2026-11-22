# 辅助功能：根据实际坐标保存图片和结果文件。
import csv
import json
import math
from pathlib import Path

def trace(commands):
    x, y, heading = 0.0, 0.0, 0.0
    segments = []
    for number, command in enumerate(commands, 1):
        rad = math.radians(heading)
        end_x = x + command["distance"] * math.cos(rad)
        end_y = y + command["distance"] * math.sin(rad)
        next_heading = (heading + (1 if command["turn"] == 0 else -1) * command["angle"]) % 360
        segments.append({"step": number, "start_x": x, "start_y": y, "end_x": end_x, "end_y": end_y,
                         "heading_before": heading, "heading_after": next_heading,
                         "rgb": command["rgb"], "distance": command["distance"]})
        x, y, heading = end_x, end_y, next_heading
    return segments



def export(commands, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    segments = trace(commands)
    fig, ax = plt.subplots(figsize=(9, 7), facecolor="#f5f7fb")
    for row in segments:
        ax.plot([row["start_x"], row["end_x"]], [row["start_y"], row["end_y"]],
                color=row["rgb"], linewidth=3, alpha=.85, solid_capstyle="round", label=f"Step {row['step']}")
        ax.annotate(str(row["step"]), ((row["start_x"] + row["end_x"])/2,
                                      (row["start_y"] + row["end_y"])/2), xytext=(7, 7), textcoords="offset points", color="#183b56")
    ax.scatter([0], [0], c="#183b56", s=40, zorder=10, label="Start (0, 0)")
    ax.set_aspect("equal")
    ax.grid(alpha=.15)
    ax.set(xlabel="x", ylabel="y", title="Automatic trajectory / 6-column commands")
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1))
    fig.tight_layout()
    for suffix in ("png", "svg"):
        fig.savefig(output / f"trajectory.{suffix}", dpi=160, bbox_inches="tight")
    plt.close(fig)
    (output / "segments.json").write_text(json.dumps(segments, ensure_ascii=False, indent=2), encoding="utf-8")
    with (output / "coordinates.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(segments[0]))
        writer.writeheader()
        writer.writerows(segments)
    page = '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>轨迹结果</title>'
    page += '<style>body{max-width:1000px;margin:30px auto;padding:15px;font-family:sans-serif}img{max-width:100%}</style>'
    page += '<h1>自动轨迹绘制</h1><p>按文件中的六条指令绘制，数字表示执行顺序。</p>'
    page += '<img src="trajectory.png" alt="六条指令绘制的轨迹">'
    page += '<p>坐标见 coordinates.csv，矢量图见 trajectory.svg。</p>'
    (output / "preview.html").write_text(page, encoding="utf-8")
    return segments
