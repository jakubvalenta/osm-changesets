import logging

import staticmaps
from celery import Celery
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER,
    broker_connection_retry_on_startup=True,
    task_time_limit=30,
)


@app.task
def render_svg(
    id: int,
    max_lat: float,
    max_lon: float,
    min_lat: float,
    min_lon: float,
    color: staticmaps.color.Color = staticmaps.color.BLUE,
    width: int = 2,
):
    logger.info("Rendering SVG for changeset %d", id)
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_OSM)
    if min_lat == max_lat and min_lon == max_lon:
        context.add_object(
            staticmaps.Marker(staticmaps.create_latlng(min_lat, min_lon), color=color),
        )
    else:
        context.add_object(
            staticmaps.Area(
                [
                    staticmaps.create_latlng(lat, lng)
                    for lat, lng in [
                        (min_lat, min_lon),
                        (min_lat, max_lon),
                        (max_lat, max_lon),
                        (max_lat, min_lon),
                        (min_lat, min_lon),
                    ]
                ],
                fill_color=staticmaps.color.TRANSPARENT,
                color=color,
                width=width,
            )
        )
    drawing = context.render_svg(800, 500)
    svg = drawing.tostring()
    cache.set(f"changeset:{id}:svg", svg, 30 * 3600)


def get_svg(id: int) -> str | None:
    return cache.get(f"changeset:{id}:svg")
