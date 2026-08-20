# Kubernetes: Helm Chart

## Что это
Helm — пакетный менеджер для Kubernetes. Chart — шаблонизированный набор
манифестов с параметрами (`values.yaml`), которые можно переопределять под
окружение (dev/stage/prod) без копирования YAML.

## Структура чарта
```
order-service/
├── Chart.yaml           # имя, версия чарта
├── values.yaml          # значения по умолчанию
├── values-prod.yaml     # переопределения для прода
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── _helpers.tpl     # общие шаблоны имён/лейблов
└── charts/               # вложенные (зависимые) чарты
```

## Пример шаблона с подстановкой значений
`values.yaml`:
```yaml
replicaCount: 3
image:
  repository: registry.internal/order-service
  tag: "1.4.2"
resources:
  requests:
    cpu: 250m
    memory: 256Mi
```

`templates/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-order-service
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - name: order-service
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

## Основные команды
```bash
helm install order-service ./order-service -f values-prod.yaml
helm upgrade order-service ./order-service -f values-prod.yaml
helm upgrade --install order-service ./order-service   # ставит либо обновляет
helm rollback order-service 2                          # откат на ревизию 2
helm history order-service
helm uninstall order-service
```

## Перед деплоем — проверить, что чарт сгенерирует
```bash
helm template order-service ./order-service -f values-prod.yaml
helm install order-service ./order-service --dry-run --debug
```
`--dry-run` не создаёт ресурсы, только показывает финальный YAML — так
ловится большинство ошибок в шаблонах до реального деплоя.

## Версионирование
`Chart.yaml` содержит `version` (версия самого чарта) и `appVersion` (версия
приложения внутри) — это разные числа, путать их не стоит.
