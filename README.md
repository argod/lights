# Lights Controllers

Controls a LED strip with a raspberry pi

the app expects the configuration file to be provided via an environment variable:

```shell
export LIGHTS_CONFIG=$CONFIG_LOCATION/config.yaml
```

it also requires `pigiod` demon to be running

```shell
sudo pigpiod
```
can run it as a standalone script:

```shell
python scripts/run_lights_controller.py
```

or as a web app with a REST API

```shell
 ../venv/bin/uvicorn lights.web_api:app --host 0.0.0.0 --port 8080 --log-config $APP_LOCATION/logging.yaml
```

supports 2 types of overlays

- Calendar (with optional connectivity to Google Calendar)
- Pomodoro Clock