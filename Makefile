INFLUX_URL ?= "https://eastus-1.azure.cloud2.influxdata.com"
INFLUX_ORG ?= "Bridgestone World Solar Challenge"
INFLUX_BUCKET ?= test

ENV_VARS=INFLUX_TOKEN INFLUX_BUCKET

export $(ENV_VARS)

.PHONY: build run

all: run

build:
	docker build -t $(DOCKER_NAME):$(DOCKER_TAG) .

run: build
	docker run -p 5000:5000 $(foreach e,$(ENV_VARS),-e $(e)) $(DOCKER_NAME)

publish: build
	docker image tag $(DOCKER_NAME):$(DOCKER_TAG) $(DOCKER_REPO)/$(DOCKER_NAME):$(DOCKER_TAG)

build/testenv: setup.cfg
		mkdir -p build
		python3 -m venv build/testenv
		source build/testenv/bin/activate && pip install -e .
		touch $@

localtest: build/testenv
		source $</bin/activate && \
			INFLUX_TOKEN=$$(cat wsc_bucket_token.key) \
		python3 \
				-m wsc_spot_poll \
				--config config-new.yaml \
						$(if $(DEBUG),--debug)

lint: build/testenv
		source $</bin/activate && \
				pip install pylint && \
				pylint $$(git ls-files '*.py')


clean:
		rm -rf build