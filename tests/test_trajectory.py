import math
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import load_commands, trace, BASE


def test_photo_commands_and_endpoints():
    commands = load_commands(BASE / "data/trajectory.csv")
    assert [c["distance"] for c in commands] == [300]*5 + [184]
    assert [c["angle"] for c in commands] == [144]*4 + [108, 72]
    rows = trace(commands)
    assert len(rows) == 6
    assert rows[0]["end_x"] == pytest.approx(300)
    assert rows[0]["end_y"] == 0
    assert rows[4]["end_x"] == pytest.approx(0, abs=1e-10)
    assert rows[4]["end_y"] == pytest.approx(0, abs=1e-10)
    assert rows[-1]["heading_after"] == 36
    for r in rows:
        assert math.hypot(r["end_x"]-r["start_x"], r["end_y"]-r["start_y"]) == pytest.approx(r["distance"])


def test_right_turn_and_headerless_input(tmp_path):
    path = tmp_path / "commands.csv"
    path.write_text("10,1,90,1,0,0\n10,0,90,0,1,0\n", encoding="utf-8")
    rows = trace(load_commands(path))
    assert rows[1]["end_x"] == pytest.approx(10)
    assert rows[1]["end_y"] == pytest.approx(-10)
    assert rows[1]["heading_after"] == 0


@pytest.mark.parametrize("data", ["", "1,2,3", "x,0,90,1,0,0", "1,2,90,1,0,0", "1,0,90,2,0,0", "nan,0,90,1,0,0", "-1,0,90,1,0,0"])
def test_invalid_commands(tmp_path, data):
    path = tmp_path / "bad.csv"
    path.write_text(data, encoding="utf-8")
    with pytest.raises(ValueError):
        load_commands(path)


def test_turtle_moves_before_turning(monkeypatch):
    from unittest.mock import Mock
    from main import draw_turtle
    turtle = Mock()
    monkeypatch.setitem(sys.modules, "turtle", turtle)
    draw_turtle([{"distance": 10, "turn": 1, "angle": 90, "rgb": (1, 0, 0)}])
    names = [call[0] for call in turtle.mock_calls]
    assert names.index("pencolor") < names.index("forward") < names.index("right")
    turtle.forward.assert_called_once_with(10)
    turtle.right.assert_called_once_with(90)
    turtle.exitonclick.assert_called_once()
