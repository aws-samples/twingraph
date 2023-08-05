docker container prune -f
docker run -d -p 5672:5672 --name=rabbitmq rabbitmq
docker run -d -p 8182:8182 --name=gremlin-server tinkerpop/gremlin-server:3.6.1
docker run --rm -d --net=host --name=gremlin-visualizer prabushitha/gremlin-visualizer:latest
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
