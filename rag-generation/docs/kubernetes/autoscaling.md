# Kubernetes: автомасштабирование (HPA)

## HorizontalPodAutoscaler — масштабирование числом реплик
Автоматически меняет число подов Deployment/StatefulSet в зависимости от
нагрузки (CPU, память или кастомные метрики).

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-service
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```
`averageUtilization: 70` — HPA держит среднюю загрузку CPU по подам около
70% от заданного в Deployment `resources.requests.cpu`. Без `requests.cpu`
в манифесте пода HPA по CPU работать не будет — не от чего считать проценты.

## Обязательное условие
HPA требует, чтобы в кластере был установлен **metrics-server** — без него
`kubectl get hpa` будет показывать `<unknown>` вместо текущей загрузки.
```bash
kubectl get hpa
kubectl top pods     # тоже требует metrics-server
```

## Масштабирование по памяти или нескольким метрикам
```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target: { type: Utilization, averageUtilization: 70 }
  - type: Resource
    resource:
      name: memory
      target: { type: Utilization, averageUtilization: 80 }
```
Если метрик несколько — HPA ориентируется на ту, что требует больше реплик.

## behavior — контроль скорости масштабирования
По умолчанию HPA может резко скейлить вниз после скачка нагрузки, что даёт
"дребезг". Ограничение скорости:
```yaml
spec:
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300   # не скейлить вниз 5 минут после пика
      policies:
        - type: Pods
          value: 1
          periodSeconds: 60             # не больше 1 пода за раз в минуту
```

## VerticalPodAutoscaler (кратко)
В отличие от HPA, VPA не меняет число подов, а подбирает `requests/limits`
для контейнера. Требует отдельной установки, конфликтует с HPA по CPU/памяти
на одном ресурсе — использовать оба одновременно на одних и тех же метриках
не стоит.
