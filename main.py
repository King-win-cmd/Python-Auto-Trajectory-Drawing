# 每行数据：距离、转向、角度、红、绿、蓝。0左转，1右转。
import argparse
import csv
import math
from pathlib import Path
from preview import trace, export

BASE = Path(__file__).resolve().parent


def load_commands(path):
    commands = []
    with open(path, encoding="utf-8-sig", newline="") as file:
        for row in csv.reader(file):
            if not row or not any(value.strip() for value in row):
                continue
            if row[0].strip() == "distance":
                continue
            if len(row) != 6:
                raise ValueError("每行要有6个数字。")
            distance, turn, angle, r, g, b = map(float, row)
            if not all(math.isfinite(x) for x in [distance, turn, angle, r, g, b]):
                raise ValueError("数据不能包含无穷或NaN。")
            if not 0 <= distance <= 1000000 or turn not in [0, 1] or not 0 <= angle <= 360:
                raise ValueError("请检查距离、转向和角度。")
            if not all(0 <= color <= 1 for color in [r, g, b]):
                raise ValueError("颜色数字应在0到1之间。")
            commands.append({"distance": distance, "turn": int(turn), "angle": angle, "rgb": (r, g, b)})
    if not commands:
        raise ValueError("文件中没有绘图数据。")
    return commands


def draw_turtle(commands):
    import turtle as t
    t.title("自动轨迹绘制，画完后单击关闭")
    t.pensize(3)
    t.speed(3)
    for row in commands:
        r, g, b = row["rgb"]
        t.pencolor(r, g, b)
        t.forward(row["distance"])
        if row["turn"] == 0:
            t.left(row["angle"])
        else:
            t.right(row["angle"])
    t.exitonclick()


def main():
    parser = argparse.ArgumentParser(description="自动轨迹绘制")
    parser.add_argument("--input", type=Path, default=BASE / "data/trajectory.csv")
    parser.add_argument("--output", type=Path, default=BASE / "outputs")
    parser.add_argument("--turtle", action="store_true")
    args = parser.parse_args()
    try:
        commands = load_commands(args.input)
        export(commands, args.output)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print("已绘制", len(commands), "条指令，结果保存在：", args.output)
    if args.turtle:
        draw_turtle(commands)


if __name__ == "__main__":
    main()
