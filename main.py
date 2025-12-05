from pathlib import Path
from random import uniform

from PIL import Image
from ursina import (
    Entity,
    Ursina,
    Vec3,
    color,
    curve,
    invoke,
    window,
)


TEXTURE_PATH = Path("textures/banana.png")


def create_pixel_texture(path: Path) -> str:
    """Create a tiny dotted texture to give the banana a pixel-art feel."""
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        return path.as_posix()

    image = Image.new("RGBA", (16, 16), (255, 255, 0, 255))
    pixels = image.load()

    # Add some brown dots to mimic banana spots.
    for _ in range(24):
        x = int(uniform(0, 15))
        y = int(uniform(0, 15))
        pixels[x, y] = (120, 80, 30, 255)

    image.save(path)
    return path.as_posix()


def build_banana(parent: Entity, texture: str) -> None:
    """Assemble a simple voxel-like banana from cubes."""
    body_positions = [
        Vec3(-0.5, -0.5, 0),
        Vec3(-0.25, -0.25, 0),
        Vec3(0, 0, 0),
        Vec3(0.25, 0.25, 0),
        Vec3(0.5, 0.5, 0),
        Vec3(0.75, 0.75, 0),
        Vec3(1.0, 0.9, 0),
        Vec3(1.1, 0.7, 0),
        Vec3(1.15, 0.45, 0),
        Vec3(1.1, 0.2, 0),
        Vec3(1.0, -0.05, 0),
        Vec3(0.8, -0.25, 0),
        Vec3(0.55, -0.45, 0),
    ]

    for pos in body_positions:
        Entity(
            parent=parent,
            model="cube",
            position=pos,
            color=color.yellow.tint(uniform(-0.1, 0.1)),
            texture=texture,
        )

    # Add the stem and bottom tip.
    Entity(
        parent=parent,
        model="cube",
        position=Vec3(-0.75, -0.75, 0),
        color=color.rgb(70, 45, 20),
    )
    Entity(
        parent=parent,
        model="cube",
        position=Vec3(1.3, 0.1, 0),
        color=color.rgb(90, 60, 30),
    )


def setup_banana(texture: str) -> Entity:
    banana = Entity()
    build_banana(banana, texture)
    banana.scale = 0.2
    banana.position = Vec3(0, 2, 3)
    return banana


def main() -> None:
    app = Ursina()

    window.color = color.rgb(25, 25, 30)
    window.title = "Growing Banana"

    texture_path = create_pixel_texture(TEXTURE_PATH)
    banana = setup_banana(texture_path)

    def reset_and_launch():
        banana.scale = 0.2
        banana.position = Vec3(0, 2, 3)
        banana.rotation = Vec3(0, 0, 0)
        invoke(grow_and_drop, delay=0.5)

    def grow_and_drop():
        banana.animate_scale(Vec3(1.2, 1.2, 1.2), duration=1.0, curve=curve.elastic_out)
        banana.animate_position(Vec3(0, -1, 1), duration=1.4, curve=curve.linear)
        banana.animate_rotation(Vec3(25, -35, 0), duration=1.4, curve=curve.linear)
        invoke(reset_and_launch, delay=3.0)

    invoke(grow_and_drop, delay=1.0)

    app.run()


if __name__ == "__main__":
    main()
