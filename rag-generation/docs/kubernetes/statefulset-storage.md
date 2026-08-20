# Kubernetes: StatefulSet и хранилище (PV/PVC)

## Когда нужен StatefulSet вместо Deployment
Для приложений с состоянием (базы данных, очереди, всё, что пишет на диск и
помнит свою "личность"). В отличие от Deployment:
- у подов стабильные имена (`postgres-0`, `postgres-1`, ...), а не случайные;
- поды создаются и удаляются по порядку, один за другим;
- у каждого пода свой персистентный том, который сохраняется при пересоздании.

## Базовый манифест
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres          # обязателен headless Service с этим именем
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 20Gi
```
`volumeClaimTemplates` — для каждого пода Kubernetes сам создаст отдельный
PersistentVolumeClaim (`data-postgres-0`, `data-postgres-1`, ...).

## PersistentVolume / PersistentVolumeClaim вручную
Когда том не создаётся автоматически через StatefulSet:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: uploads-storage
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: standard
  resources:
    requests:
      storage: 10Gi
```
```yaml
volumes:
  - name: uploads
    persistentVolumeClaim:
      claimName: uploads-storage
```

## accessModes
- `ReadWriteOnce` — том монтируется в один под на чтение/запись (обычный
  случай для баз данных);
- `ReadWriteMany` — несколько подов одновременно на чтение/запись, доступно
  не у всех storage-классов (NFS, некоторые облачные);
- `ReadOnlyMany` — несколько подов только на чтение.

## Частая ошибка
При удалении StatefulSet тома **не удаляются** — это осознанная защита от
потери данных. Если нужно действительно очистить хранилище:
```bash
kubectl delete statefulset postgres
kubectl delete pvc -l app=postgres
```
