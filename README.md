# lightbulb
rabbitmq connection through docker command - 
docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 rabbitmq:3-management

running celery worker - celery -A lightbulb worker -l info --pool=solo
running celery beat - celery -A lightbulb beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
