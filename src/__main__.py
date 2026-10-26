from src.api.setup import init_faststream_app, init_taskiq_v1
from src.api.v1.setup import init_app_v1
from src.core.settings import PROJECT_NAME, PROJECT_VERSION, load_settings
from src.core.uvicorn_server import run_api_uvicorn

settings = load_settings()
broker, scheduler = init_taskiq_v1(settings)

_, faststream = init_faststream_app(settings)


def main() -> None:
    app = init_app_v1(
        settings, title=PROJECT_NAME, version=PROJECT_VERSION, broker=broker
    )
    run_api_uvicorn(app, settings)


if __name__ == "__main__":
    main()
