# Kubernetes: ConfigMap и Secret

## ConfigMap — нечувствительная конфигурация
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-service-config
data:
  LOG_LEVEL: "info"
  DEFAULT_PAGE_SIZE: "50"
  application.yaml: |
    server:
      port: 8080
    feature:
      newCheckout: true
```

## Secret — пароли, токены, сертификаты
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: order-service-secrets
type: Opaque
stringData:
  DB_PASSWORD: "supersecret"
  API_TOKEN: "sk-xxxxxxxx"
```
`stringData` — можно писать значения в открытом виде, Kubernetes сам
закодирует в base64 при сохранении. Поле `data` требует уже закодированных
значений — им пользуются реже, руками кодировать не нужно.

Secret по умолчанию хранится в etcd в base64 — **это не шифрование**, а
кодирование. Для реальной защиты нужен либо шифрованный etcd, либо внешний
секрет-менеджер (Vault, sealed-secrets, external-secrets-operator).

## Как подключить к поду

### Как переменные окружения
```yaml
containers:
  - name: order-service
    envFrom:
      - configMapRef:
          name: order-service-config
      - secretRef:
          name: order-service-secrets
```

### Точечно, одну переменную
```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: order-service-secrets
        key: DB_PASSWORD
```

### Как файл (volume)
```yaml
volumes:
  - name: config
    configMap:
      name: order-service-config
containers:
  - name: order-service
    volumeMounts:
      - name: config
        mountPath: /app/config
```
Так удобнее для конфигов вида `application.yaml`, которые приложение читает
как файл, а не через env.

## Важно
Изменение ConfigMap/Secret **не перезапускает** уже запущенные поды
автоматически. Если переменные подключены через `env`/`envFrom`, нужен ручной
rollout:
```bash
kubectl rollout restart deployment/order-service
```
Файлы, смонтированные через volume, обновляются в поде сами (с задержкой в
несколько минут), но приложение обычно нужно перечитать конфиг вручную или
тоже перезапустить.
