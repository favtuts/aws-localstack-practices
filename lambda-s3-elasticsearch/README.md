# Using LocalStack to test AWS services locally
* https://tuts.heomi.net/using-localstack-to-test-aws-services-locally/

# Setting up LocalStack

Create `docker-compose.yml` file which contains the Localstack and Elasticsearch:
```yaml
version: "3.9"

services:
  elasticsearch:
    container_name: elasticsearch
    image: docker.elastic.co/elasticsearch/elasticsearch:7.10.2 # Max version supported by LocalStack
    environment:
      - node.name=elasticsearch
      - cluster.name=es-docker-cluster
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - data01:/usr/share/elasticsearch/data

  localstack:
    container_name: "${LOCALSTACK_DOCKER_NAME-localstack_main}"
    image: localstack/localstack
    ports:
      - "4566:4566" # Edge port
    depends_on:
      - elasticsearch
    environment:
      - DEBUG=1
      - OPENSEARCH_ENDPOINT_STRATEGY=port # port, path, domain
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "${LOCALSTACK_VOLUME_DIR:-./volume}:/var/lib/localstack"
      - "/var/run/docker.sock:/var/run/docker.sock"

volumes:
  data01:
    driver: local
```

To run the stack:
```
$ docker compose up
```

To stop the stack
```
$ docker compose down
```

# Key tools required:
* Node.js (brew install node)
* LocalStack (brew install localstack)
* Python (brew install python) this is required to install `awscli-local`
* `awscli-local` (`pip install awscli-local`) this avoids having to define the endpoint-url on each command

