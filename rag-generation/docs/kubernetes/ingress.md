# Kubernetes: Ingress

## Что это
Ingress — правила маршрутизации HTTP(S)-трафика извне кластера к внутренним
Service по домену и пути. Сам по себе Ingress ничего не делает — нужен
Ingress Controller (nginx-ingress, traefik и т.п.), который эти правила читает.

## Базовый манифест (nginx-ingress)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: order-service
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: orders.internal.company.ru
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: order-service
                port:
                  number: 80
```

## Несколько сервисов по путям
```yaml
spec:
  rules:
    - host: api.internal.company.ru
      http:
        paths:
          - path: /orders
            pathType: Prefix
            backend:
              service:
                name: order-service
                port: { number: 80 }
          - path: /users
            pathType: Prefix
            backend:
              service:
                name: user-service
                port: { number: 80 }
```

## TLS
```yaml
spec:
  tls:
    - hosts:
        - orders.internal.company.ru
      secretName: orders-tls
```
Сертификат кладётся в Secret типа `kubernetes.io/tls`. Для автоматизации
обычно ставят cert-manager, который сам выпускает и обновляет сертификаты.

## Частые проблемы
- **404 от самого Ingress Controller** — не совпал `host` в запросе с `host`
  в правиле, либо не тот `ingressClassName`, если в кластере несколько
  контроллеров;
- **502/504** — Service существует, но за ним нет готовых (`Ready`) подов;
- изменения в аннотациях контроллера применяются не мгновенно — если правило
  не подхватилось, смотреть логи самого ingress-controller pod'а, а не
  приложения.
