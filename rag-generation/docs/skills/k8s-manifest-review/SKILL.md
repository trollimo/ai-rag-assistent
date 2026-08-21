---
name: k8s-manifest-review
description: Проверяет Kubernetes-манифесты на типовые ошибки конфигурации перед деплоем — отсутствие лимитов ресурсов, probes, некорректные selector'ы.
version: 1.0.0
---

# K8s Manifest Review Skill

Статическая проверка YAML-манифестов Kubernetes на соответствие внутренним
стандартам (см. `rag-generation/docs/kubernetes/` в базе знаний) до того, как
манифест уйдёт в деплой.

## Когда применять

Перед `kubectl apply` или мёрджем PR с изменениями в `k8s/`, `helm/templates/`.

## Как использовать

1. Запустить `scripts/validate.sh <путь-к-манифестам>`.
2. Свериться с `references/checklist.md` — что именно проверяется и почему.
3. Для найденных проблем — использовать формулировки из
   `references/common-issues.md` как основу комментария в PR.

## Что проверяется

- `resources.requests` / `resources.limits` заданы у каждого контейнера;
- `livenessProbe` и `readinessProbe` присутствуют;
- `selector.matchLabels` совпадает с `template.metadata.labels`;
- образ не использует тег `latest`.
