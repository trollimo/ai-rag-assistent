# Kubernetes: Service

## Что это
Service даёт подам с одинаковым label стабильный сетевой адрес — сами поды
пересоздаются и меняют IP, Service остаётся неизменным.

## Типы Service

### ClusterIP (по умолчанию)
Доступен только внутри кластера. Стандарт для связи между сервисами.
```yaml
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  type: ClusterIP
  selector:
    app: order-service
  ports:
    - port: 80
      targetPort: 8080
```
`port` — порт самого Service, `targetPort` — порт в контейнере. Они могут
отличаться.

### NodePort
Открывает порт на каждой ноде кластера (диапазон 30000-32767). Используется
редко, обычно только для отладки — в проде трафик заводят через Ingress.

### LoadBalancer
Заказывает внешний балансировщик у облачного провайдера. Для on-prem кластеров
без облака — не сработает без дополнительного контроллера (MetalLB и т.п.).

### Headless (`clusterIP: None`)
Не балансирует — вместо одного IP отдаёт DNS-записи всех подов напрямую.
Нужен для StatefulSet, когда важно обращаться к конкретной реплике (базы данных).
```yaml
spec:
  clusterIP: None
  selector:
    app: postgres
```

## DNS внутри кластера
Сервис доступен по имени `<service>.<namespace>.svc.cluster.local`, внутри
одного namespace достаточно короткого имени `order-service`.

## Частая ошибка
`selector` в Service должен точно совпадать с `labels` в шаблоне пода
Deployment'а — иначе Service не найдёт ни одного пода и будет отдавать
пустой endpoint. Проверка:
```bash
kubectl get endpoints order-service
```
Если список пуст — селектор не совпадает с лейблами подов.
