# Kubernetes: Deployment

## Что это
Deployment управляет набором одинаковых Pod'ов: следит, чтобы нужное число реплик
было запущено, и умеет обновлять их без простоя (rolling update).

## Базовый манифест
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  labels:
    app: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
        - name: order-service
          image: registry.internal/order-service:1.4.2
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
```

## Обязательно указывать
- **requests/limits** — без них Pod может занять всю память ноды и уронить соседей;
- **readinessProbe** и **livenessProbe** — иначе трафик пойдёт на ещё не готовый под;
- **imagePullPolicy: IfNotPresent** для стабильных тегов, `Always` — для `:latest`
  (в проде тег `:latest` вообще не использовать).

## Пробы
```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 20
```

## Rolling update
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```
`maxUnavailable` — сколько подов может быть недоступно во время выката,
`maxSurge` — сколько можно поднять сверх нормы. `1/1` — безопасный дефолт для
большинства сервисов.

## Полезные команды
```bash
kubectl rollout status deployment/order-service
kubectl rollout undo deployment/order-service          # откат на предыдущую версию
kubectl rollout history deployment/order-service
kubectl scale deployment/order-service --replicas=5
```
