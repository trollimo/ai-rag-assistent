# Kubernetes: PodDisruptionBudget

## Что это
PodDisruptionBudget (PDB) ограничивает, сколько подов приложения может быть
недоступно одновременно при *добровольных* нарушениях — сливе ноды (`kubectl
drain`), обновлении кластера, автоскейлинге узлов вниз. На падение ноды или
OOM-kill PDB не влияет: это недобровольные нарушения.

## Базовый манифест
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-service-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: order-service
```

Вместо `minAvailable` можно задать `maxUnavailable` — но не оба сразу.

## Типовые ошибки

**PDB без запаса реплик.** `minAvailable: 2` при `replicas: 2` делает слив ноды
невозможным: Kubernetes не имеет права выселить ни один под и `kubectl drain`
зависает навсегда. Держите `minAvailable` строго меньше числа реплик.

**Проценты вместо чисел на маленьких деплойментах.** `minAvailable: 50%` при
трёх репликах округляется вверх до 2 — не всегда то, что ожидают.

**Селектор не совпадает с деплойментом.** PDB с чужим или пустым `selector`
молча не защищает ничего. Проверяйте `kubectl get pdb` — колонка
`ALLOWED DISRUPTIONS` покажет реальное состояние.
