import math
import argparse

parser = argparse.ArgumentParser("python visualize.py")
parser.add_argument(
    "--log",
    required=False,
    help="Set verbosity level of logging.",
    default="ERROR",
    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    type=str,
)
args = parser.parse_args()

import logging

logging.basicConfig(encoding="utf-8")
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, args.log.upper()))

import cairo
import PIL.Image


class Hoop:
    def __init__(self, sets: list) -> None:
        self.sets = sets
        self.unique_elements = set().union(*sets)
        self.ordered_elements = list(self.unique_elements)
        self.n = len(self.unique_elements)
        logger.debug("%d unqiue elements found", self.n)

        self.highlighted_element = None
        self.highlighted_set = None

    def _render(
        self, width: int = 1024, height: int = 1024, highlighted_element: object = None, highlighted_set: object = None, path : str = None
    ) -> None:
        COLOR_THEME = {
            0: "#D00000",
            1: "#E85D04",
            2: "#FFBA08",
            3: "#9FA167",
            4: "#3F88C5",
            5: "#215A84",
            6: "#032B43",
            7: "#0B4D53",
            8: "#136F63",
        }
        INNER_RADIUS = 0.05
        OUTER_RADIUS = 0.45
        FRAME_WIDTH = 0.001
        ELEMENT_WIDTH = 0.02
        HIGHLIGHT_WIDTH = 0.004
        FRAME_COLOR = (0, 0, 0)
        GRID_COLOR = (0.5, 0.5, 0.5)
        HIGHLIGHT_COLOR = (0.5, 0.5, 0.5, 0.3)

        if path is None:
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        else:
            self.surface = cairo.SVGSurface(path, width, height)
        ctx = cairo.Context(self.surface)
        ctx.scale(width, height)

        ctx.set_source_rgba(1, 1, 1)
        ctx.rectangle(0, 0, 1, 1)
        ctx.fill()

        ctx.set_source_rgb(*FRAME_COLOR)
        ctx.set_line_width(FRAME_WIDTH)
        ctx.arc(0.5, 0.5, INNER_RADIUS, 0, 2 * math.pi)
        ctx.stroke()
        ctx.arc(0.5, 0.5, OUTER_RADIUS, 0, 2 * math.pi)
        ctx.stroke()

        ctx.set_source_rgb(*GRID_COLOR)
        grid_radius_step_size = (OUTER_RADIUS - INNER_RADIUS) / self.n
        for i in range(1, self.n):
            ctx.arc(0.5, 0.5, INNER_RADIUS + i * grid_radius_step_size, 0, 2 * math.pi)
            ctx.stroke()

        if (
            highlighted_element in self.unique_elements
            and highlighted_element is not None
        ):
            idx = self.ordered_elements.index(highlighted_element)
            ctx.set_dash([1, 0])
            ctx.set_line_width(grid_radius_step_size)
            ctx.set_source_rgba(*HIGHLIGHT_COLOR)
            ctx.arc(
                0.5,
                0.5,
                INNER_RADIUS + (idx + 0.5) * grid_radius_step_size,
                0,
                2 * math.pi,
            )
            ctx.stroke()

        N = len(self.sets)
        set_size = (2 * math.pi) / N

        ctx.set_source_rgba(*HIGHLIGHT_COLOR)
        ctx.set_line_width(grid_radius_step_size)
        if highlighted_set in self.sets and highlighted_set is not None:
            idx = self.sets.index(highlighted_set)
            for i in range(self.n):
                ctx.arc(
                        0.5,
                        0.5,
                        INNER_RADIUS + (i + 0.5) * grid_radius_step_size,
                        (idx - 0.5) * set_size,
                        (idx + 0.5) * set_size,
                    )
                ctx.stroke()


        ctx.set_line_width(ELEMENT_WIDTH)
        for i, s in enumerate(self.sets):
            for e in s:
                idx = self.ordered_elements.index(e)
                ctx.set_source_rgb(
                    *tuple(
                        int(COLOR_THEME[idx].strip("#")[j : j + 2], 16) / 255
                        for j in (0, 2, 4)
                    )
                )
                ctx.arc(
                    0.5,
                    0.5,
                    INNER_RADIUS + (idx + 0.5) * grid_radius_step_size,
                    (i - 0.5) * set_size,
                    (i + 0.5) * set_size,
                )
                ctx.stroke()

        ctx.set_source_rgb(*FRAME_COLOR)
        ctx.set_line_width(FRAME_WIDTH)
        for i in range(len(self.sets)):
            ctx.save()
            ctx.translate(0.5, 0.5)
            ctx.rotate(set_size * i - 0.5 * set_size)
            ctx.move_to(0, INNER_RADIUS)
            ctx.line_to(0, OUTER_RADIUS)
            ctx.stroke()
            ctx.restore()

        ctx.set_line_width(HIGHLIGHT_WIDTH)
        ctx.set_dash([0.01])
        ctx.set_source_rgb(*GRID_COLOR)
        if (
            highlighted_element in self.unique_elements
            and highlighted_element is not None
        ):
            idx = self.ordered_elements.index(highlighted_element)
            ctx.arc(
                0.5, 0.5, INNER_RADIUS + idx * grid_radius_step_size, 0, 2 * math.pi
            )
            ctx.stroke()
            ctx.arc(
                0.5,
                0.5,
                INNER_RADIUS + (idx + 1) * grid_radius_step_size,
                0,
                2 * math.pi,
            )
            ctx.stroke()

        if highlighted_set in self.sets and highlighted_set is not None:
            idx = self.sets.index(highlighted_set)

            ctx.arc(
                0.5, 0.5, INNER_RADIUS, (idx - 0.5) * set_size, (idx + 0.5) * set_size
            )
            ctx.stroke()
            ctx.arc(
                0.5, 0.5, OUTER_RADIUS, (idx - 0.5) * set_size, (idx + 0.5) * set_size
            )
            ctx.stroke()
            for i in range(idx-1, idx + 1):
                ctx.save()
                ctx.translate(0.5, 0.5)
                ctx.rotate(set_size * i - 0.5 * set_size)
                ctx.move_to(0, INNER_RADIUS)
                ctx.line_to(0, OUTER_RADIUS)
                ctx.stroke()
                ctx.restore()

    def highlight_element(self, highlighted_element: object) -> None:
        if highlighted_element in self.unique_elements:
            self.highlighted_element = highlighted_element
            self.highlighted_set = None

    def highlight_set(self, highlighted_set: set) -> None:
        if highlighted_set in self.sets:
            self.highlighted_set = highlighted_set
            self.highlighted_element = None

    def show(self, width: int = 1024, height: int = 1024) -> None:
        self._render(width=width, height=height, highlighted_element=self.highlighted_element, highlighted_set=self.highlighted_set)
        size = (self.surface.get_width(), self.surface.get_height())
        stride = self.surface.get_stride()
        with self.surface.get_data() as memory:
            image = PIL.Image.frombuffer(
                "RGBA", size, memory.tobytes(), "raw", "BGRa", stride
            )
        image.show()

    def save(self, path: str, width: int = 1024, height: int = 1024) -> None:
        self._render(width=width, height=height, highlighted_element=self.highlighted_element, highlighted_set=self.highlighted_set, path=path)


if __name__ == "__main__":
    import os

    d = Hoop(sets=[{1, 2}, {3, 4}, {1, 3, 5}, {1, 5}])
    d.save(os.path.join("assets", "standard.svg"), width=256, height=256)
    d.highlight_element(5)
    d.save(os.path.join("assets", "highlighted_element.svg"), width=256, height=256)
    d.highlight_set({1, 2})
    d.save(os.path.join("assets", "highlighted_set.svg"), width=256, height=256)
    d.show()
